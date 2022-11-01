import music.search.services as services
import music.adapters.repository as repo
from flask import Blueprint, render_template, url_for, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, DataRequired

searchBlueprint = Blueprint('searchBp', __name__)


@searchBlueprint.route('/search', methods=['POST', 'GET'])
def searchResult():
    if request.method == "POST":
        query = request.form.get("search")
        all_track = services.searchTracks(query, repo.repo_instance)
    else:
        query = request.args.get('search')
        query = query.strip()
        all_track = services.searchTracks(query, repo.repo_instance)

    page_number = request.args.get('page_number')
    total_pages = len(all_track)//24
    previous_page = 0

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
        next_url = url_for("searchBp.searchResult", search=query, page_number=next_page)
    if previous_page != page_number:
        previous_url = url_for("searchBp.searchResult", search=query, page_number=previous_page)
    first_url = url_for('searchBp.searchResult', search=query, page_number=0)
    last_url = url_for('searchBp.searchResult', search=query, page_number=len(all_track) // 24)

    tracks_for_display = all_track[page_number * 24: (page_number + 1) * 24]

    return render_template('search/searchResult.html', all_the_track=tracks_for_display, fav_tracks=fav_tracks,
                           page_number=page_number, next_url=next_url, previous_url=previous_url,
                           first_url=first_url,
                           last_url=last_url,
                           query=query, total_pages=total_pages)


class SearchForm(FlaskForm):
    query = StringField("Query", [DataRequired(), Length(min=1)])
    submit = SubmitField('Search')
