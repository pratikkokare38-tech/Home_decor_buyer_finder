import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Unified REST Framework exception handler.
    Guarantees all API errors return structured JSON with actionable error messages
    instead of raw HTML 500 pages.
    """
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(response.data, dict) and 'error' not in response.data:
            detail = response.data.get('detail')
            if not detail:
                detail = "; ".join([f"{k}: {v}" for k, v in response.data.items()])
            response.data = {
                'error': {
                    'code': 'API_ERROR',
                    'message': str(detail)
                }
            }
        return response

    # Unhandled 500 server exception: Log and return JSON
    view_name = context.get('view').__class__.__name__ if context.get('view') else 'UnknownView'
    logger.exception("Unhandled 500 server error in view %s: %s", view_name, exc)

    return Response({
        'error': {
            'code': 'INTERNAL_SERVER_ERROR',
            'message': f"Server error: {str(exc)}"
        }
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
