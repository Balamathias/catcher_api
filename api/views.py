from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.decorators import api_view
from supabase import Client

from utils.response import ResponseMixin
from typing import Any, Dict, Optional, List, Tuple, cast
from django.utils import timezone
import os
import uuid
import requests


class ItemsAPIView(APIView, ResponseMixin):
    permission_classes = []

    @staticmethod
    def _parse_int(value, default):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _coerce_fee(value: Any) -> Optional[float]:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _coerce_images(value: Any) -> Optional[List[str]]:
        if value is None:
            return None
        if isinstance(value, list):
            return [str(v) for v in value]
        # allow comma-separated string
        if isinstance(value, str):
            parts = [p.strip() for p in value.split(',') if p.strip()]
            return parts if parts else None
        return None

    @staticmethod
    def _validate_status(value: Any) -> Optional[str]:
        if value is None:
            return None
        allowed = {"safe", "stolen", "unknown"}
        v = str(value).lower()
        return v if v in allowed else None

    def _build_payload(self, data: Dict[str, Any], *, require_required_fields: bool) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Extract and validate fields for the items table from request data.

        Returns: (payload, error)
        """
        name = (data.get("name") or "").strip()
        serial_number = (data.get("serial_number") or "").strip()

        if require_required_fields:
            missing = []
            if not name:
                missing.append("name")
            if not serial_number:
                missing.append("serial_number")
            if missing:
                return None, {
                    "detail": "Missing required field(s)",
                    "fields": missing,
                }

        payload: Dict[str, Any] = {}
        if name:
            payload["name"] = name
        if serial_number:
            payload["serial_number"] = serial_number

        # Optional fields
        if "description" in data:
            payload["description"] = data.get("description")
        if "category" in data:
            payload["category"] = data.get("category")
        if "contact_info" in data:
            payload["contact_info"] = data.get("contact_info")
        if "owner" in data:
            payload["owner"] = data.get("owner")
        if "image_url" in data:
            payload["image_url"] = data.get("image_url")
        if "images" in data:
            payload["images"] = self._coerce_images(data.get("images"))
        if "fee" in data:
            payload["fee"] = self._coerce_fee(data.get("fee"))
        if "status" in data:
            status_val = self._validate_status(data.get("status"))
            if status_val is None:
                return None, {"detail": "Invalid status. Must be one of: safe, stolen, unknown"}
            payload["status"] = status_val

        # Always update timestamp on mutations if column exists
        payload["updated_at"] = timezone.now().isoformat()

        return payload, None

    def get(self, request, item_id=None):
        """
        GET /items/  —  return paginated item history
        GET /items/<id>/  —  return specific item details

        Query params (for list view):
            - limit: number of records to return (default: 30)
            - offset: number of records to skip (default: 0)
            - query: search query to filter items by name or description.
        """
        try:
            user = request.user
            if not getattr(user, "is_authenticated", False):
                return self.response(
                    error="Authentication required",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

            supabase: Client = request.supabase_client

            if item_id is not None:
                try:
                    item_id = int(item_id)
                except (TypeError, ValueError):
                    return self.response(
                        error={"detail": "Invalid item id"},
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                response = (
                    supabase.table('items')
                    .select('*')
                    .eq('id', item_id)
                    .eq('user_id', str(user.id))
                    .single()
                    .execute()
                )

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

            limit = self._parse_int(request.query_params.get('limit'), 30)
            offset = self._parse_int(request.query_params.get('offset'), 0)
            query = (request.query_params.get('query') or '').strip()

            count_q = (
                supabase.table('items')
                .select('*', count='exact')  # type: ignore[arg-type]
                .eq('user_id', str(user.id))
            )

            data_q = (
                supabase.table('items')
                .select('*')
                .eq('user_id', str(user.id))
            )

            if query:
                pattern = f"%{query}%"
                or_clause = f"name.ilike.{pattern},description.ilike.{pattern}"
                count_q = count_q.or_(or_clause)
                data_q = data_q.or_(or_clause)

            count_response = count_q.execute()
            total_count = count_response.count or 0

            response = (
                data_q
                .order('created_at', desc=True)
                .range(offset, max(offset + limit - 1, offset))
                .execute()
            )

            next_offset = offset + limit if (offset + limit) < total_count else None
            prev_offset = offset - limit if offset > 0 else None

            return self.response(
                data=response.data or [],
                count=total_count,
                next=next_offset,
                previous=prev_offset,
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            print(e)
            return self.response(
                error={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="An unknown error occurred"
            )

    def post(self, request):
        """
        POST /items/ — create a new item for the authenticated user.
        Required: name, serial_number
        Optional: description, category, contact_info, owner, image_url, images[], fee, status
        """
        try:
            user = request.user
            if not getattr(user, "is_authenticated", False):
                return self.response(
                    error="Authentication required",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            supabase: Client = request.supabase_client
            payload, err = self._build_payload(request.data, require_required_fields=True)
            if err:
                return self.response(
                    error=err,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            if payload is None:
                return self.response(
                    error={"detail": "Invalid payload"},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            payload = cast(Dict[str, Any], payload)

            # server-side ownership
            payload["user_id"] = str(user.id)

            response = (
                supabase.table('items')
                .insert(payload)
                .execute()
            )

            data = None
            if response and getattr(response, 'data', None):
                # supabase returns list for insert
                if isinstance(response.data, list) and response.data:
                    data = response.data[0]
                else:
                    data = response.data

            # Fallback: fetch latest by serial_number and user
            if not data:
                sel = (
                    supabase.table('items')
                    .select('*')
                    .eq('user_id', str(user.id))
                    .eq('serial_number', payload['serial_number'])
                    .order('created_at', desc=True)
                    .limit(1)
                    .execute()
                )
                data = (sel.data or [None])[0]

            return self.response(
                data=data,
                status_code=status.HTTP_201_CREATED,
                message="Item created successfully.",
            )

        except Exception as e:
            print(e)
            return self.response(
                error={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to create item",
            )

    def patch(self, request, item_id=None):
        """PATCH /items/<id>/ — partial update for an item owned by the user."""
        try:
            user = request.user
            if not getattr(user, "is_authenticated", False):
                return self.response(
                    error="Authentication required",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            if item_id is None:
                return self.response(
                    error={"detail": "Item id is required"},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            supabase: Client = request.supabase_client

            # Ensure the item exists and belongs to the user
            existing = (
                supabase.table('items')
                .select('*')
                .eq('id', item_id)
                .eq('user_id', str(user.id))
                .single()
                .execute()
            )
            if not existing.data:
                return self.response(
                    error={"detail": "Item not found"},
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            payload, err = self._build_payload(request.data, require_required_fields=False)
            if err:
                return self.response(
                    error=err,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            if not payload:
                return self.response(
                    error={"detail": "No valid fields to update"},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            resp = (
                supabase.table('items')
                .update(payload)
                .eq('id', item_id)
                .eq('user_id', str(user.id))
                .execute()
            )

            data = None
            if resp and getattr(resp, 'data', None):
                data = resp.data[0] if isinstance(resp.data, list) and resp.data else resp.data
            else:
                # re-fetch
                refetch = (
                    supabase.table('items')
                    .select('*')
                    .eq('id', item_id)
                    .eq('user_id', str(user.id))
                    .single()
                    .execute()
                )
                data = refetch.data

            return self.response(
                data=data,
                status_code=status.HTTP_200_OK,
                message="Item updated successfully.",
            )

        except Exception as e:
            print(e)
            return self.response(
                error={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to update item",
            )

    def put(self, request, item_id=None):
        """PUT /items/<id>/ — full update; requires required fields."""
        return self._put_or_patch(request, item_id, require_required_fields=True)

    def _put_or_patch(self, request, item_id: Optional[int], require_required_fields: bool):
        # Reuse patch logic but toggle requirement
        try:
            user = request.user
            if not getattr(user, "is_authenticated", False):
                return self.response(
                    error="Authentication required",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            if item_id is None:
                return self.response(
                    error={"detail": "Item id is required"},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            
            supabase: Client = request.supabase_client

            existing = (
                supabase.table('items')
                .select('*')
                .eq('id', item_id)
                .eq('user_id', str(user.id))
                .single()
                .execute()
            )
            if not existing.data:
                return self.response(
                    error={"detail": "Item not found"},
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            payload, err = self._build_payload(request.data, require_required_fields=require_required_fields)
            if err:
                return self.response(
                    error=err,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            if not payload:
                return self.response(
                    error={"detail": "No valid fields to update"},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            resp = (
                supabase.table('items')
                .update(payload)
                .eq('id', item_id)
                .eq('user_id', str(user.id))
                .execute()
            )

            data = None
            if resp and getattr(resp, 'data', None):
                data = resp.data[0] if isinstance(resp.data, list) and resp.data else resp.data
            else:
                refetch = (
                    supabase.table('items')
                    .select('*')
                    .eq('id', item_id)
                    .eq('user_id', str(user.id))
                    .single()
                    .execute()
                )
                data = refetch.data

            return self.response(
                data=data,
                status_code=status.HTTP_200_OK,
                message="Item updated successfully.",
            )
        except Exception as e:
            print(e)
            return self.response(
                error={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to update item",
            )

    def delete(self, request, item_id=None):
        """DELETE /items/<id>/ — delete an item owned by the user."""
        try:
            user = request.user
            if not getattr(user, "is_authenticated", False):
                return self.response(
                    error="Authentication required",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            if item_id is None:
                return self.response(
                    error={"detail": "Item id is required"},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            supabase: Client = request.supabase_client

            # Ensure ownership and existence first
            existing = (
                supabase.table('items')
                .select('id')
                .eq('id', item_id)
                .eq('user_id', str(user.id))
                .single()
                .execute()
            )
            if not existing.data:
                return self.response(
                    error={"detail": "Item not found"},
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            _ = (
                supabase.table('items')
                .delete()
                .eq('id', item_id)
                .eq('user_id', str(user.id))
                .execute()
            )

            return self.response(
                data={"id": item_id},
                status_code=status.HTTP_200_OK,
                message="Item deleted successfully.",
            )
        except Exception as e:
            print(e)
            return self.response(
                error={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to delete item",
            )


class SearchRegistry(APIView, ResponseMixin):
    """
    POST /search_registry/
    {
        "query": "bike",
        "category": "electronics",    # optional
        "status": "stolen",           # optional, one of: safe, stolen, unknown
        "serial_number": "12345",     # optional, exact match
        "limit": 30,                  # optional
        "offset": 0                   # optional
    }
    Returns a paginated list of items matching the search across the entire registry (all users).
    """
    permission_classes = []

    def post(self, request):
        try:
            supabase: Client = request.supabase_client
            data = request.data or {}

            query = (data.get("query") or "").strip()
            category = (data.get("category") or "").strip()
            status_val = (data.get("status") or "").strip().lower()
            serial_number = (data.get("serial_number") or "").strip()
            limit = ItemsAPIView._parse_int(data.get("limit"), 30)
            offset = ItemsAPIView._parse_int(data.get("offset"), 0)

            q = supabase.table("items").select("*", count="exact")  # type: ignore[arg-type]

            if query:
                pattern = f"%{query}%"
                or_clause = f"name.ilike.{pattern},description.ilike.{pattern},category.ilike.{pattern},serial_number.ilike.{pattern}"
                q = q.or_(or_clause)

            if category:
                q = q.eq("category", category)

            if status_val:
                allowed = {"safe", "stolen", "unknown"}
                if status_val not in allowed:
                    return self.response(
                        error={"detail": "Invalid status. Must be one of: safe, stolen, unknown"},
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
                q = q.eq("status", status_val)

            if serial_number:
                q = q.eq("serial_number", serial_number)

            count_response = q.execute()
            total_count = count_response.count or 0

            q = q.order("created_at", desc=True).range(offset, max(offset + limit - 1, offset))
            response = q.execute()

            next_offset = offset + limit if (offset + limit) < total_count else None
            prev_offset = offset - limit if offset > 0 else None

            return self.response(
                data=response.data or [],
                count=total_count,
                next=next_offset,
                previous=prev_offset,
                status_code=status.HTTP_200_OK,
                message="Registry search completed.",
            )

        except Exception as e:
            print(e)
            return self.response(
                error={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to search registry",
            )


def health_check(request):
    """
    Health check endpoint.
    """
    return JsonResponse({"status": "ok"})


class ItemsAnalyticsAPIView(APIView, ResponseMixin):
    """
    GET /items/analytics/ — Returns per-user analytics summary for items.

    Response data shape:
    {
      "totals": { "total": int, "safe": int, "stolen": int, "unknown": int },
      "ratios": { "safe": float, "stolen": float, "unknown": float },
      "last_updated_at": string | null,
      "recent": { "added_last_30d": int, "stolen_last_30d": int },
      "top_categories": [{ "category": string, "count": int }],
      "recent_items": [ items (limited fields) ]
    }
    """
    permission_classes = []

    def get(self, request):
        try:
            user = request.user
            if not getattr(user, "is_authenticated", False):
                return self.response(
                    error="Authentication required",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            supabase: Client = request.supabase_client
            user_id = str(user.id)

            # Totals
            total_resp = (
                supabase.table("items")
                .select("id", count="exact")  # type: ignore[arg-type]
                .eq("user_id", user_id)
                .limit(0)
                .execute()
            )
            total = total_resp.count or 0

            def _count_status(s: str) -> int:
                r = (
                    supabase.table("items")
                    .select("id", count="exact")  # type: ignore[arg-type]
                    .eq("user_id", user_id)
                    .eq("status", s)
                    .limit(0)
                    .execute()
                )
                return r.count or 0

            safe_count = _count_status("safe")
            stolen_count = _count_status("stolen")
            unknown_count = _count_status("unknown")

            # Last updated timestamp
            last_updated_sel = (
                supabase.table("items")
                .select("updated_at")
                .eq("user_id", user_id)
                .order("updated_at", desc=True)
                .limit(1)
                .execute()
            )
            last_updated_at = (last_updated_sel.data or [{}])[0].get("updated_at") if last_updated_sel and getattr(last_updated_sel, "data", None) else None

            # Recent activity (last 30 days)
            thirty_days_ago = (timezone.now() - timezone.timedelta(days=30)).isoformat()
            added_30_resp = (
                supabase.table("items")
                .select("id", count="exact")  # type: ignore[arg-type]
                .eq("user_id", user_id)
                .gte("created_at", thirty_days_ago)
                .limit(0)
                .execute()
            )
            added_last_30d = added_30_resp.count or 0

            stolen_30_resp = (
                supabase.table("items")
                .select("id", count="exact")  # type: ignore[arg-type]
                .eq("user_id", user_id)
                .eq("status", "stolen")
                .gte("created_at", thirty_days_ago)
                .limit(0)
                .execute()
            )
            stolen_last_30d = stolen_30_resp.count or 0

            # Top categories (simple aggregation in Python)
            cats_resp = (
                supabase.table("items")
                .select("category")
                .eq("user_id", user_id)
                .execute()
            )
            category_counts: Dict[str, int] = {}
            for row in (cats_resp.data or []):
                cat = (row or {}).get("category")
                if not cat:
                    continue
                cat = str(cat)
                category_counts[cat] = category_counts.get(cat, 0) + 1
            top_categories = sorted(
                (
                    {"category": k, "count": v}
                    for k, v in category_counts.items()
                ),
                key=lambda x: x["count"],
                reverse=True,
            )[:5]

            # Recent items (limit 5)
            recent_fields = "id,name,status,category,created_at,image_url,serial_number"
            recent_resp = (
                supabase.table("items")
                .select(recent_fields)
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(5)
                .execute()
            )
            recent_items = recent_resp.data or []

            # Ratios
            def pct(n: int) -> float:
                return round((n / total) * 100.0, 2) if total > 0 else 0.0

            data = {
                "totals": {
                    "total": total,
                    "safe": safe_count,
                    "stolen": stolen_count,
                    "unknown": unknown_count,
                },
                "ratios": {
                    "safe": pct(safe_count),
                    "stolen": pct(stolen_count),
                    "unknown": pct(unknown_count),
                },
                "last_updated_at": last_updated_at,
                "recent": {
                    "added_last_30d": added_last_30d,
                    "stolen_last_30d": stolen_last_30d,
                },
                "top_categories": top_categories,
                "recent_items": recent_items,
            }

            return self.response(
                data=data,
                status_code=status.HTTP_200_OK,
                message="Items analytics fetched successfully.",
            )
        except Exception as e:
            print(e)
            return self.response(
                error={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to fetch analytics",
            )


class PaystackPaymentAPIView(APIView, ResponseMixin):
    """
    POST /payments/initiate/  -> initialize a paystack transaction for fixed fee
    GET  /payments/verify/    -> verify a paystack transaction by reference

    Environment variables required:
      - PAYSTACK_SECRET_KEY
    Optional:
      - PAYSTACK_CALLBACK_URL (used by Paystack to redirect after payment)
    """
    permission_classes = []

    FEE_NGN = 100  # ₦100 as requested

    def post(self, request):
        """Initialize transaction and return authorization_url and reference."""
        try:
            user = request.user
            if not getattr(user, "is_authenticated", False):
                return self.response(
                    error="Authentication required",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            secret_key = os.environ.get("PAYSTACK_SECRET_KEY")
            if not secret_key:
                return self.response(
                    error={"detail": "PAYSTACK_SECRET_KEY not configured on server"},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            data = request.data or {}
            email = (data.get("email") or "").strip()
            if not email:
                return self.response(
                    error={"detail": "Email is required for payment initialization"},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Always compute amount server-side to avoid tampering
            amount_kobo = self.FEE_NGN * 100
            reference = f"{user.id}-{uuid.uuid4().hex[:12]}"
            callback_url = os.environ.get("PAYSTACK_CALLBACK_URL")

            payload = {
                "email": email,
                "amount": amount_kobo,
                "currency": "NGN",
                "reference": reference,
            }
            if callback_url:
                payload["callback_url"] = callback_url

            headers = {
                "Authorization": f"Bearer {secret_key}",
                "Content-Type": "application/json",
            }
            resp = requests.post(
                "https://api.paystack.co/transaction/initialize",
                json=payload,
                headers=headers,
                timeout=30,
            )
            j = resp.json()
            if not j.get("status"):
                message = (j.get("message") or "Failed to initialize payment")
                return self.response(
                    error={"detail": message, "payload": j},
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=message,
                )

            data_out = j.get("data") or {}
            return self.response(
                data={
                    "authorization_url": data_out.get("authorization_url"),
                    "access_code": data_out.get("access_code"),
                    "reference": data_out.get("reference") or reference,
                    "amount": amount_kobo,
                },
                status_code=status.HTTP_200_OK,
                message="Payment initialized",
            )
        except Exception as e:
            print(e)
            return self.response(
                error={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to initialize payment",
            )

    def get(self, request):
        """Verify a transaction by reference (?reference=...)."""
        try:
            user = request.user
            if not getattr(user, "is_authenticated", False):
                return self.response(
                    error="Authentication required",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            secret_key = os.environ.get("PAYSTACK_SECRET_KEY")
            if not secret_key:
                return self.response(
                    error={"detail": "PAYSTACK_SECRET_KEY not configured on server"},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            reference = (request.query_params.get("reference") or "").strip()
            if not reference:
                return self.response(
                    error={"detail": "reference is required"},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            headers = {"Authorization": f"Bearer {secret_key}"}
            url = f"https://api.paystack.co/transaction/verify/{reference}"
            resp = requests.get(url, headers=headers, timeout=30)
            j = resp.json()
            if not j.get("status"):
                return self.response(
                    error={"detail": j.get("message"), "payload": j},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            data_out = j.get("data") or {}
            status_str = (data_out.get("status") or "").lower()
            amount = int(data_out.get("amount") or 0)
            verified = status_str == "success" and amount >= (self.FEE_NGN * 100)

            return self.response(
                data={
                    "verified": verified,
                    "status": status_str,
                    "amount": amount,
                    "reference": reference,
                    "gateway_response": data_out.get("gateway_response"),
                    "paid_at": data_out.get("paid_at"),
                    "channel": data_out.get("channel"),
                },
                status_code=status.HTTP_200_OK,
                message="Verification complete",
            )
        except Exception as e:
            print(e)
            return self.response(
                error={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Failed to verify payment",
            )
