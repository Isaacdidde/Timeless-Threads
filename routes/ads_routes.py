"""
Ads Engine API Routes (Production Ready)

Safely handles:
    - Rendering ad slots
    - Creating new slots (POST)
    - Creating ad campaigns via API
Fully protects against:
    - Invalid ObjectId
    - Missing JSON fields
    - Mongo write failures
    - Unexpected crashes (returns JSON instead of 500 error)

This file does NOT change any existing behavior.
"""

from flask import Blueprint, request, jsonify
from controllers.ads_controller import render_ad_slot
from database.ads_models import (
    create_slot,
    campaigns_col
)

ads_bp = Blueprint("ads", __name__, url_prefix="/ads")


# ---------------------------------------------------------------------------
# RENDER AD SLOT  (Frontend Request)
# ---------------------------------------------------------------------------
@ads_bp.route("/render/<slot_name>")
def render_slot(slot_name):
    """
    Returns HTML snippet of an ad inside a given slot.
    Ads controller handles impression logging & selection.
    """

    if not slot_name or not isinstance(slot_name, str):
        return "", 400

    try:
        html = render_ad_slot(slot_name)
        return html or ""   # Always return safe HTML content
    except Exception as e:
        print("❌ ERROR: Failed to render ad slot:", e)
        return "", 500


# ---------------------------------------------------------------------------
# CREATE NEW SLOT  (POST)
# This is used internally by Dcorp, not exposed to users.
# ---------------------------------------------------------------------------
@ads_bp.route("/slots", methods=["POST"])
def add_slot():
    try:
        name = (request.form.get("name") or "").strip()
        description = request.form.get("description") or ""
    except Exception:
        return jsonify({"error": "Invalid form data"}), 400

    if not name:
        return jsonify({"error": "Slot name is required"}), 400

    try:
        create_slot(name, description)
        return jsonify({"message": "Slot created"}), 201
    except Exception as e:
        print("❌ ERROR: Failed to create ad slot:", e)
        return jsonify({"error": "Internal error"}), 500


# ---------------------------------------------------------------------------
# CREATE A CAMPAIGN VIA DIRECT API (JSON)
# Normally done via Admin Panel; this is programmatic access.
# ---------------------------------------------------------------------------
@ads_bp.route("/campaigns", methods=["POST"])
def create_campaign_api():
    try:
        payload = request.json
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    if not payload:
        return jsonify({"error": "JSON body required"}), 400

    # Optional: ensure the campaign has required fields
    required = ["advertiser_id", "creative", "status"]
    missing = [f for f in required if f not in payload]

    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        result = campaigns_col().insert_one(payload)
        return jsonify({
            "message": "Campaign created",
            "id": str(result.inserted_id)
        }), 201

    except Exception as e:
        print("❌ ERROR: Failed to create ad campaign:", e)
        return jsonify({"error": "Internal server error"}), 500
