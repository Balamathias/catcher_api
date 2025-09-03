from rest_framework.views import APIView
from rest_framework import status

from utils.response import ResponseMixin


class ItemsAPIView(APIView, ResponseMixin):
    
    permission_classes = []

    def get(self, request, item_id=None):
        """
        GET /items/  —  return paginated item history
        GET /items/<id>/  —  return specific item details

        Query params (for list view):
            - limit: number of records to return (default: 30)
            - offset: number of records to skip (default: 0)
        """
        try:
            user = request.user
            if not user:
                return self.response(
                    error="Authentication required",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

            supabase = request.supabase_client

            if item_id:
                response = supabase.table('items')\
                    .select('*')\
                    .eq('id', int(item_id))\
                    .eq('user', user.id)\
                    .single()\
                    .execute()

                if not response.data:
                    return self.response(
                        error={"detail": "Item not found"},
                        status_code=status.HTTP_404_NOT_FOUND,
                        message="Item could not be found."
                    )

                return self.response(
                    data=response.data,
                    status_code=status.HTTP_200_OK,
                    message="Item retrieved successfully."
                )

            limit = int(request.query_params.get('limit', 30))
            offset = int(request.query_params.get('offset', 0))

            count_response = supabase.table('items').select('*', count='exact').eq('user', user.id).execute()
            total_count = count_response.count

            response = supabase.table('items')\
                .select('*')\
                .eq('user', user.id)\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return self.response(
                data=response.data,
                count=total_count,
                next=offset + limit if offset + limit < total_count else None,
                previous=offset - limit if offset > 0 else None,
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            print(e)
            return self.response(
                error={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="An unknown error occurred"
            )

