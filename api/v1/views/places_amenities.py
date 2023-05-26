#!/usr/bin/python3
""" Configures RESTful api for the places_amenities route """
from flask import jsonify, request, abort
from api.v1.views import app_views
from models import storage


@app_views.route("places/<place_id>/amenities", methods=["GET"], strict_slashes=False)
def places_amenities(place_id):
    """ configures the places_amenities route """

    place = storage.get("Place", place_id)
    if not place:
        abort(404)

    places_amenities = place.amenities
    amenities_dict = [amenity.to_dict() for amenity in places_amenities]

    return jsonify(amenities_dict)


@app_views.route("places/<place_id>/amenities/<amenity_id>",
                 methods=["DELETE", "POST"], strict_slashes=False)
def amenities_id(place_id, amenity_id):
    """ configures the places/<place_id>/amenities/<amenity_id> route """

    place = storage.get("Place", place_id)
    amenity = storage.get("Amenity", amenity_id)

    if not amenity or not place:
        abort(404)

    if request.method == "DELETE":
        if amenity.place_id != place_id:
            abort(404)

        storage.delete(amenity)
        storage.save()

        return jsonify({}), 200
    else:
        if amenity.place_id == place_id:
            return jsonify(amenity.to_dict()), 200

        amenity.place_id = place_id
        storage.save()

        return jsonify(amenity.to_dict()), 201
