from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .utils import plan_event_from_llm, get_user_events, update_event, delete_event, get_event_by_id
from bson import ObjectId

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_event(request):
    user = request.user
    event_description = request.data.get("description")  # User provides only description
    
    if not event_description:
        return Response({"error": "Event description is required"}, status=400)

    try:
        event = plan_event_from_llm(user, event_description)
        event.save()
        return Response({"success": True, "event_id": str(event.id)})
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_events(request):
    user = request.user
    events = get_user_events(user)
    res = []
    for e in events:
        res.append({
            "id": str(e.id),
            "title": e.title,
            "description": e.description,
            "event_type": e.event_type,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "related_task": str(e.related_task.id) if e.related_task else None
        })
    return Response(res)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def event_detail(request, event_id):
    e = get_event_by_id(request.user, event_id)
    if not e:
        return Response({"error": "Event not found"}, status=404)

    return Response({
        "id": str(e.id),
        "title": e.title,
        "description": e.description,
        "event_type": e.event_type,
        "start_time": e.start_time,
        "end_time": e.end_time,
        "related_task": str(e.related_task.id) if e.related_task else None
    })


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def edit_event(request):
    event_id = request.data.get("id")
    updates = request.data.get("update", {})

    e = update_event(request.user, event_id, updates)
    if not e:
        return Response({"error": "Event not found"}, status=404)

    return Response({"success": True})


# @api_view(["DELETE"])
# @permission_classes([IsAuthenticated])
# def remove_event(request):
#     event_id = request.data.get("id")
#     ok = delete_event(request.user, event_id)
#     if not ok:
#         return Response({"error": "Event not found"}, status=404)
#     return Response({"success": True})

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_event(request, event_id):  # ID comes from URL, not body
    ok = delete_event(request.user, event_id)
    if not ok:
        return Response({"error": "Event not found"}, status=404)
    return Response({"success": True})