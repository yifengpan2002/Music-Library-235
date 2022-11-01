from flask import Blueprint, render_template, url_for, request, session, redirect
import music.favorites.services as services
import music.adapters.repository as repo

favorite_blueprint = Blueprint(
    'faveBp', __name__)


@favorite_blueprint.route('/favorites')
def display_fav_tracks():
    try:
        user_name = session['user_name']
        user = services.get_user(user_name, repo.repo_instance)
        display_tracks = user.liked_tracks
        if len(display_tracks) == 0:
            return render_template('favorites/empty.html')
        else:
            return render_template('favorites/favorites.html', user=user.user_name, all_the_track=display_tracks)

    except KeyError:
        return render_template('favorites/error.html')

    except AttributeError:
        return render_template('favorites/error.html')


@favorite_blueprint.route('/added')
def added():
    track_list = services.get_all_tracks(repo.repo_instance)

    try:
        user_name = session['user_name']
        if user_name is not None or user_name != "":
            user = services.get_user(user_name, repo.repo_instance)
            track = request.args.get("track")
            track = services.find_track(track, track_list)
            user.add_liked_track(track)
            return render_template('favorites/track_message.html', track=track.title, message="has been added to your "
                                                                                              "favourites!")

    except KeyError:
        return render_template('favorites/error.html')

    except AttributeError:
        return render_template('favorites/error.html')


@favorite_blueprint.route('/removed')
def removed():
    track_list = services.get_all_tracks(repo.repo_instance)
    user_name = session['user_name']
    user = services.get_user(user_name, repo.repo_instance)
    track = request.args.get("track")
    track = services.find_track(track, track_list)
    user.remove_liked_track(track)
    return render_template('favorites/track_message.html', track=track.title, message="has been removed from your "
                                                                                      "favourites!")
