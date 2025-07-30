import http
import mimetypes
import os

import quizcomp.constants
import quizcomp.converter.convert
import quizcomp.katex
import quizcomp.latex
import quizcomp.pdf
import quizcomp.project
import quizcomp.question.base
import quizcomp.quiz
import quizcomp.util.dirent
import quizcomp.util.file
import quizcomp.util.json

import qcg.util.dirent

# Compiled output filename extensions will take the value of the format if not overwritten here.
OVERRIDE_EXTENSIONS = {
    'canvas': 'canvas.html',
}

def fetch(handler, path, project_dir, **kwargs):
    tree = qcg.util.dirent.tree(project_dir)
    _augment_tree(tree, project_dir)

    data = {
        'project': quizcomp.project.Project.from_path(project_dir).to_pod(),
        'tree': tree,
        'dirname': os.path.basename(project_dir),
        'supportedFeatures': {
            'pdf': quizcomp.latex.is_available(),
            'htmlEquations': quizcomp.katex.is_available(),
        },
    }

    return data, None, None

def fetch_file(handler, path, project_dir, relpath = None, **kwargs):
    file_path = _rel_file_check(project_dir, relpath)
    if (not isinstance(file_path, str)):
        return file_path

    return _create_api_file(file_path, relpath), None, None

def save_file(handler, path, project_dir, relpath = None, content = None, **kwargs):
    file_path = _rel_file_check(project_dir, relpath)
    if (not isinstance(file_path, str)):
        return file_path

    if (content is None):
        return "Missing 'content'.", http.HTTPStatus.BAD_REQUEST, None

    quizcomp.util.file.from_base64(content, file_path)

    data = {
        'relpath': relpath,
    }

    return data, None, None

def compile(handler, path, project_dir, relpath = None, formats = None, **kwargs):
    file_path = _rel_file_check(project_dir, relpath)
    if (not isinstance(file_path, str)):
        return file_path

    if (formats is None):
        return "Missing 'formats'.", http.HTTPStatus.BAD_REQUEST, None

    result = {}
    for format in formats:
        data, success = _compile(file_path, format)
        if (not success):
            return f"Compile failed for '{relpath}' ({format}): '{data}'.", http.HTTPStatus.BAD_REQUEST, None

        data['relpath'] = relpath

        result[format] = data

    return result, None, None

def _rel_file_check(project_dir, relpath):
    """
    Standard checks for a relpath that points to a file.
    Returns the resolved path on sucess, or a standard HTTP result tuple on failure.
    """

    if (relpath is None):
        return "Missing 'relpath'.", http.HTTPStatus.BAD_REQUEST, None

    file_path = _resolve_relpath(project_dir, relpath)

    if (not os.path.exists(file_path)):
        return "Relative path '%s' does not exist." % (relpath), http.HTTPStatus.BAD_REQUEST, None

    if (not os.path.isfile(file_path)):
        return "Relative path '%s' is not a file." % (relpath), http.HTTPStatus.BAD_REQUEST, None

    return file_path

def _resolve_relpath(project_dir, relpath):
    """
    Resolve the relative path (which has URL-style path separators ('/')) to an abs path.
    """

    relpath = relpath.strip().removeprefix('/')

    # Split on URL-style path separators and replace with system ones.
    # Note that dirent names with '/' are not allowed.
    relpath = os.sep.join(relpath.split('/'))

    return os.path.abspath(os.path.join(project_dir, relpath))

def _create_api_file(path, relpath):
    content = quizcomp.util.file.to_base64(path)
    mime, _ = mimetypes.guess_type(path)
    filename = os.path.basename(path)

    return {
        'relpath': relpath,
        'content': content,
        'mime': mime,
        'filename': filename,
    }

def _augment_tree(root, parent_real_path, parent_relpath = None):
    """
    Augment the basic file tree with project/quizcomp information.
    """

    if (root is None):
        return root

    real_path = os.path.join(parent_real_path, root['name'])

    relpath = root['name']
    if (parent_relpath is not None):
        # relpaths use URL-style path separators.
        relpath = f"{parent_relpath}/{relpath}"

    root['relpath'] = relpath

    # If this is a file, check its type and return.
    if (root['type'] == 'file'):
        if (root['name'].lower().endswith('.json')):
            root['objectType'] = _guess_object_type(real_path)

        return

    # Potential compile targets.
    # A compile target is the quiz/question that should be compiled
    # when this dirent is selected and the compile button is pressed.
    # { base name (without extension): relpath, ...}
    compile_targets = {}

    for dirent in root.get('dirents', []):
        _augment_tree(dirent, real_path, relpath)

        # Now that this dirent has been aurmented, check if it is a compile target.
        if (dirent.get('objectType') in ['quiz', 'question']):
            compile_targets[os.path.splitext(dirent['name'])[0]] = dirent['relpath']

    # Associate the appropriate compile target with a file (not dir).
    # If there is only one compile target, all files in this dir get that compile target.
    # If there are multiple compile targets, then the target will need to have a matching base name (no extension).
    for dirent in root.get('dirents', []):
        if (dirent['type'] != 'file'):
            continue

        if (len(compile_targets) == 0):
            continue

        compile_target = None
        if (len(compile_targets) == 1):
            compile_target = list(compile_targets.values())[0]
        else:
            compile_target = compile_targets.get(os.path.splitext(dirent['name'])[0], None)

        if (compile_target is not None):
            dirent['compileTarget'] = compile_target

def _guess_object_type(path):
    """
    Given a path a to JSON file, guess what type of QuizComp object it represents.
    Will return either on of quizcomp.constants.JSON_OBJECT_TYPES or None.
    """

    data = quizcomp.util.json.load_path(path)

    # First, look at the 'type' field.
    type = data.get('type', None)
    if (type in quizcomp.constants.JSON_OBJECT_TYPES):
        return type

    # Try to guess based on other attributes.

    if ('title' in data):
        return quizcomp.constants.TYPE_QUIZ

    if ('question_type' in data):
        return quizcomp.constants.TYPE_QUESTION

    return None

def _compile(path, format):
    type = _guess_object_type(path)
    if (type is None):
        return "Unable to determine type of QuizComp object.", False

    if (type not in [quizcomp.constants.TYPE_QUIZ, quizcomp.constants.TYPE_QUESTION]):
        return f"Only quiz and questions can be compiled, found '{type}'.", False

    base_name = type

    if (type == quizcomp.constants.TYPE_QUIZ):

        if (format == 'pdf'):
            content, base_name = _make_pdf(path)
        else:
            quiz = quizcomp.quiz.Quiz.from_path(path)
            base_name = quiz.title

            variant = quiz.create_variant()

            content = quizcomp.converter.convert.convert_variant(variant, format = format)
    else:
        question = quizcomp.question.base.Question.from_path(path)
        content = quizcomp.converter.convert.convert_question(question, format = format)

        if (question.name != ''):
            base_name = question.name

    extension = OVERRIDE_EXTENSIONS.get(format, format)
    name = base_name + '.' + extension
    mime, _ = mimetypes.guess_type(name)

    data = {
        'filename': name,
        'mime': mime,
        'content': quizcomp.util.encoding.to_base64(content),
    }

    return data, True

def _make_pdf(path):
    temp_dir = quizcomp.util.dirent.get_temp_path('qcg-pdf-')
    quiz, _, _ = quizcomp.pdf.make_with_path(path, skip_key = True, base_out_dir = temp_dir)

    out_path = os.path.join(temp_dir, quiz.title, f"{quiz.title}.pdf")
    if (not os.path.isfile(out_path)):
        raise ValueError(f"Unable to find PDF output in: '{out_path}'.")

    with open(out_path, 'rb') as file:
        data = file.read()

    return data, quiz.title
