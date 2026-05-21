from flask import (
    Blueprint, current_app, jsonify, redirect, render_template, request,
    Response, url_for
)


chore_bp = Blueprint('chore_bp', __name__)


@chore_bp.route('/chores', methods=['GET', 'POST'])
def add_chore() -> Response:
    """Add a new chore.

    If the request method is POST, add the chore and redirect to the home page.
    Otherwise, render the add chore template.

    Returns:
        Union[Response, str]: The rendered template or a redirect response.
    """
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        current_app.chore_service.add_chore(name, description)
        return redirect(url_for('index_bp.home'))

    return render_template('add_chore.html')


@chore_bp.route('/chore/<int:chore_id>/complete', methods=['POST'])
def complete_chore(chore_id: int) -> Response:
    """Mark a chore as complete.

    Args:
        chore_id (int): The ID of the chore to complete.

    Returns:
        Union[Response, tuple]: A redirect response or a JSON error message.
    """
    chore = current_app.chore_service.get_chore_by_id(chore_id)
    if not chore:
        return jsonify({'error': 'Chore not found'}), 404

    current_app.chore_service.complete_chore(chore)
    return redirect(url_for('chore_bp.get_chore', chore_id=chore.id))


@chore_bp.route('/delete_chore/<int:chore_id>', methods=['POST'])
def delete_chore(chore_id: int) -> Response:
    """Delete a chore.

    Args:
        chore_id (int): The ID of the chore to delete.

    Returns:
        Union[Response, tuple]: A redirect response or a JSON error message.
    """
    chore = current_app.chore_service.get_chore_by_id(chore_id)
    if not chore:
        return jsonify({'error': 'Chore not found'}), 404

    current_app.chore_service.delete_chore(chore_id)
    return redirect(url_for('index_bp.home'))


@chore_bp.route('/chores/<int:chore_id>/edit', methods=['GET', 'POST'])
def edit_chore(chore_id: int) -> Response:
    """Edit a chore.

    If the request method is POST, update the chore and redirect to the chore
    detail page. Otherwise, render the edit chore template.

    Args:
        chore_id (int): The ID of the chore to edit.

    Returns:
        Union[Response, str, tuple]: The rendered template, a redirect response,
            or a JSON error message.
    """
    chore = current_app.chore_service.get_chore_by_id(chore_id)
    if not chore:
        return jsonify({'error': 'Chore not found'}), 404

    if request.method == 'POST':
        chore.name = request.form['name']
        chore.description = request.form['description']
        assigned_to = request.form.get('assigned_to')
        chore.person_id = int(assigned_to) if assigned_to else None
        current_app.chore_service.update_chore(chore)
        return redirect(url_for('chore_bp.get_chore', chore_id=chore.id))

    people = current_app.people_service.get_all_people()
    return render_template('edit_chore.html', chore=chore, people=people)


@chore_bp.route('/chores/<int:chore_id>', methods=['GET'])
def get_chore(chore_id: int) -> Response:
    """Get a specific chore by ID.

    Args:
        chore_id (int): The ID of the chore to retrieve.

    Returns:
        Union[Response, str, tuple]: The rendered template with the chore
            details, or a JSON error message.
    """
    chore = current_app.chore_service.get_chore_by_id(chore_id)
    if chore:
        return render_template('chore_detail.html', chore=chore)
    else:
        return jsonify({'error': 'Chore not found'}), 404
