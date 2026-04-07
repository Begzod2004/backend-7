from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsKattaOmborAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('ADMIN', 'KATTA_OMBOR_ADMINI')


class IsKichikOmborAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'KICHIK_OMBOR_ADMINI'


class IsHisobchi(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'HISOBCHI'


class IsAdminOrKattaOmborAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('ADMIN', 'KATTA_OMBOR_ADMINI')


class IsAdminOrKattaOrKichik(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            'ADMIN', 'KATTA_OMBOR_ADMINI', 'KICHIK_OMBOR_ADMINI'
        )


class IsAdminOrKattaOrHisobchi(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            'ADMIN', 'KATTA_OMBOR_ADMINI', 'HISOBCHI'
        )


class CanManageInvoices(BasePermission):
    """HISOBCHI, ADMIN, KATTA_OMBOR_ADMINI can manage invoices."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            'ADMIN', 'KATTA_OMBOR_ADMINI', 'HISOBCHI'
        )


class CanViewAll(BasePermission):
    """HISOBCHI can only view, not modify."""
    def has_permission(self, request, view):
        if request.user.role == 'HISOBCHI':
            return request.method in ('GET', 'HEAD', 'OPTIONS')
        return request.user.is_authenticated
