#!/usr/bin/python3
""" Configures RESTful api for the places route """
from flask import jsonify, request, abort
from api.v1.views import app_views
from models import storage
from models.place import Place


@app_views.route("cities/<city_id>/places", methods=["GET", "POST"],
                 strict_slashes=False)
def places(city_id):
    """ configures the places route """

    city = storage.get("City", city_id)
    if not city:
        abort(404)

    if request.method == "GET":
        places_dict = [place.to_dict() for place in city.places]

        return jsonify(places_dict)
    else:
        try:
            json_dict = request.get_json()
        except Exception:
            abort(400, "Not a JSON")

        if not json_dict:
            abort(400, "Not a JSON")

        try:
            user_id = json_dict["user_id"]
        except KeyError:
            abort(400, "Missing user_id")

        user = storage.get("User", user_id)
        if not user:
            abort(404)

        try:
            name = json_dict["name"]
        except KeyError:
            abort(400, "Missing name")

        new_place = Place(**json_dict)
        new_place.city_id = city_id

        storage.new(new_place)
        storage.save()

        return jsonify(new_place.to_dict()), 201


@app_views.route("/places/<place_id>", methods=["GET", "DELETE", "PUT"],
                 strict_slashes=False)
def places_id(place_id):
    """ configures the places/<place_id> route """

    place = storage.get("Place", place_id)

    if not place:
        abort(404)

    if request.method == "GET":
        return jsonify(place.to_dict())
    elif request.method == "DELETE":
        storage.delete(place)
        storage.save()

        return jsonify({}), 200
    else:
        try:
            json_dict = request.get_json()
        except Exception:
            abort(400, "Not a JSON")

        if not json_dict:
            abort(400, "Not a JSON")

        keys_to_ignore = [
                "id", "user_id", "city_id",
                "created_at", "updated_at"
        ]
        for key, val in json_dict.items():
            if key not in keys_to_ignore:
                setattr(place, key, val)

        storage.save()
        return jsonify(place.to_dict()), 200


@app_views.route("/places_search", methods=["POST"], strict_slashes=False)
def places_search():
    """ configures route for places_search """

    try:
        json_dict = request.get_json()
    except Exception:
        abort(400, "Not a JSON")

    places = storage.all(Place)
    places_dict = [place.to_dict() for place in places.values()]

    if not json_dict:
        return jsonify(places_dict)

    if not json_dict.get("states") and (
            not json_dict.get("cities")) and (
            not json_dict.get("amenities")):
        return jsonify(places_dict)

    result = []

    if json_dict.get("states"):
        for state_id in json_dict["states"]:
            state = storage.get("State", state_id)
            if state:
                for city in state.cities:
                    for place in city.places:
                        if place not in result:
                            result.append(place)

    if json_dict.get("cities"):
        for city_id in json_dict["cities"]:
            city = storage.get("City", city_id)
            if city:
                for place in city.places:
                    if place not in result:
                        result.append(place)

    if json_dict.get("amenities"):
        if not result:
            result = [place for place in places.values()]
        filtered = []
        amenities = []
        for amenity_id in json_dict["amenities"]:
            amenities.append(storage.get("Amenity", amenity_id))

        for place in result:
            place_amenities = place.amenities
            has_all = True
            for amenity in amenities:
                if amenity not in place_amenities:
                    has_all = False
                    break

            if has_all:
                filtered.append(place)

        filtered_dict = []
        for place in filtered:
            place_dict = place.to_dict()
            if "amenities" in place_dict:
                del place_dict["amenities"]
            filtered_dict.append(place_dict)

        return jsonify(filtered_dict)

    result_dict = [place.to_dict() for place in result]

    return jsonify(result_dict)
