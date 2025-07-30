class AuditError(Exception):
    """审计模块内部错误"""
    pass

class PermissionError(Exception):
    """权限检查模块内部错误"""
    pass
