from flask import Blueprint, render_template, url_for, request, session, redirect
import music.browse.services as services
import music.adapters.repository as repo
from music.authentication.authentication import login_required
from music.domainmodel.review import Review
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange

browse_blueprint = Blueprint(
    'browse_bp', __name__)


@browse_blueprint.route('/display_all_tracks')
def display_all_tracks():
    all_track = services.get_all_tracks(repo.repo_instance)
    page_number = request.args.get('page_number')
    genre = request.args.get('genre_name')
    artist_name = request.args.get('artist_name')
    album_title = request.args.get('album_name')
    fav_tracks = []
    try:
        user_name = session['user_name']
        if user_name is not None:
            user = services.get_user(user_name, repo.repo_instance)
            fav_tracks = user.liked_tracks

    except KeyError:
        pass

    except AttributeError:
        pass

    if genre is not None:
        all_track = services.display_specific_genre_track(genre, repo.repo_instance)

    if artist_name is not None:
        all_track = services.display_specific_artist_track(artist_name, repo.repo_instance)

    if album_title is not None:
        all_track = services.display_specific_album_track(album_title, repo.repo_instance)

    previous_page = 0
    total_pages = len(all_track) // 24
    if page_number is None:
        page_number = 0
    else:
        page_number = int(page_number)

    if page_number > 0:
        previous_page = page_number - 1
    if len(all_track) > page_number * 24 + 24:
        next_page = page_number + 1
    else:
        next_page = page_number

    next_url = None
    previous_url = None

    if next_page != page_number:
        next_url = url_for("browse_bp.display_all_tracks", page_number=next_page, genre_name=genre,
                           artist_name=artist_name, album_name=album_title)
    if previous_page != page_number:
        previous_url = url_for("browse_bp.display_all_tracks", page_number=previous_page, genre_name=genre,
                               artist_name=artist_name, album_name=album_title)
    first_url = url_for('browse_bp.display_all_tracks', page_number=0, genre_name=genre, artist_name=artist_name,
                        album_name=album_title)
    last_url = url_for('browse_bp.display_all_tracks', page_number=len(all_track) // 24, genre_name=genre,
                       artist_name=artist_name, album_name=album_title)

    tracks_for_display = all_track[page_number * 24: (page_number + 1) * 24]
    return render_template('browse/browse.html', all_the_track=tracks_for_display, genre_name=genre,
                           fav_tracks=fav_tracks, page_number=page_number, next_url=next_url, previous_url=previous_url,
                           first_url=first_url, last_url=last_url, total_pages=total_pages, fav_track=fav_tracks,
                           artist_name=artist_name, album_name=album_title, length=len(all_track))


@browse_blueprint.route('/display_all_genres')
def display_all_genres():
    all_genre = repo.repo_instance.get_all_genres()
    unique_genre_list = list()
    for e in all_genre:
        if e.name not in unique_genre_list:
            unique_genre_list.append(e)
    return render_template("browse/genre.html", all_genre=unique_genre_list)


@browse_blueprint.route('/display_all_artists')
def display_all_artists():
    all_artist = repo.repo_instance.get_all_artists()
    unique_artist_list = list()
    for e in all_artist:
        if e.full_name not in unique_artist_list:
            unique_artist_list.append(e)
    return render_template("browse/artist.html", all_artist=unique_artist_list)


@browse_blueprint.route('/display_all_albums')
def display_all_albums():
    all_album = repo.repo_instance.get_all_albums()
    unique_album_list = list()
    for e in all_album:
        if e not in unique_album_list:
            unique_album_list.append(e)
    return render_template("browse/album.html", all_album=unique_album_list)


@browse_blueprint.route('/comment', methods=['GET', 'POST'])
@login_required
def comment_on_article():
    username = session["user_name"]
    user = repo.repo_instance.get_user(username)
    if user is None:
        return redirect(url_for('authBp.login'))
    id = request.args.get('id')
    title = request.args.get('title')
    all_track = services.get_all_tracks(repo.repo_instance)
    review_on_this_track = list()
    track = services.search_track(id, title, repo.repo_instance)
    form = CommentForm()
    if form.validate_on_submit():
        review = Review(track, form.comment.data, form.rating.data)
        user.add_review(review)
        for comment in user.reviews:
            if comment.track.__eq__(track):
                review_on_this_track.append(comment)
        return render_template("browse/simple_track.html", all_user_comment=review_on_this_track, track=track,
                               form=form)
    return render_template("browse/simple_track.html", all_user_comment=review_on_this_track, track=track,
                           form=form)


class CommentForm(FlaskForm):
    rating = IntegerField("Rating", [
        DataRequired(),
        NumberRange(min=0, max=5, message="Rating number must be 0 - 5")
    ])
    comment = TextAreaField('Comment', [
        DataRequired(),
        Length(min=4, message='Your comment is too short')
    ])
    submit = SubmitField('Post Review')
