import json
from functools import wraps
import traceback
import jwt

from utils.myLogger import infoLog
from config import settings
from user.model.user import UserMode

res = {"code": 401, 'result':  '身份认证信息不正确'}
res_no_authorization = {"code": 401, 'result':  'no_authorization'}
res_no_user = {"code": 401, 'result':  '员工不存在'}
res_fun = {"code": 401, 'result':  '方法体运行出错'}
res_signature = {"code": 401, 'result':  '身份认证已过期'}
res_format = {"code": 401, 'result': '身份认证信息填写不正确，格式为：JWT token。'}
res_owner = {"code": 401, 'result':  '角色与访问权限不匹配'}
res_admin = {"code": 401, 'result':  '需要管理员权限'}


def authenticated(verify_is_admin=False, role = None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                Authorization = self.request.headers.get(
                    'Authorization', None
                )
            except Exception as e:
                infoLog.error(traceback.format_exc())
                self.set_status(401)
                self.finish(res_format)
            try:
                Authorization = Authorization.split(' ')
                if len(Authorization) != 2:
                    self.set_status(401)
                    self.finish(res_format)
                    return None
                else:
                    if Authorization[0] != 'JWT':
                        self.set_status(401)
                        self.finish(res_format)
                        return None
            except Exception as e:
                infoLog.error(traceback.format_exc())
                self.set_status(401)
                self.finish(res_format)
                return None

            Authorization = Authorization[1]

            if Authorization:

                try:
                    data = jwt.decode(
                        Authorization, settings.settings["secret_key"], leeway=settings.settings['jwt_expire'],
                        options={"verify_exp": True}
                    )

                    user_id = data['id']

                    try:
                        user = UserMode.queryUserId(user_id)
                        if user is None:
                            self.set_status(401)
                            self.finish(res_no_user)
                            return None

                        if verify_is_admin:
                            if not user.isAdmin == 1:
                                self.set_status(401)
                                self.finish(res_admin)
                                return
                        else:
                            if (not user.isAdmin == 1) and role:
                                if user.groName not in role:
                                    self.set_status(402)
                                    self.finish(res_owner)
                                    return None
                        self._current_user = user

                        try:
                            return func(self, *args, **kwargs)
                        except Exception as e:
                            infoLog.error(traceback.format_exc())
                            self.set_status(401)
                            self.finish(res_fun)
                            return None
                    except Exception as e:
                        infoLog.error(traceback.format_exc())
                        self.set_status(401)
                        self.finish(res)
                        return None
                except jwt.exceptions.ExpiredSignatureError as e:
                    infoLog.error(traceback.format_exc())
                    self.set_status(401)
                    self.finish(res_signature)
                    return None
                except jwt.exceptions.DecodeError as e:
                    infoLog.error(traceback.format_exc())
                    self.set_status(401)
                    self.finish(res)
                    return None
            else:
                self.set_status(401)
                self.finish(res_no_authorization)
                return None

        return wrapper
    return decorator

if __name__ == '__main__':
    v = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6ImYzOWU5ZTljLTRmODItNGU3My1iMDBiLWVkODM3M2UyNzU0ZCIsInVzZXJuYW1lIjoiYWRtaW4iLCJleHAiOjE1ODY5MzI2NTl9.Mc3aIBbnuIRVEcB5SjMOIqaT2bllMSrfVFb4N-E4DVs'
    data = jwt.decode(
        v, "d#aPr8%mssTZgVGy", leeway=7 * 24 * 3600,
        options={"verify_exp": True}
    )
    print(data)