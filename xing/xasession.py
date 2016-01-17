# -*- coding: utf-8 -*-
import time
import pythoncom
import win32com.client
from xing import xacom
from xing.xaquery import Query
from xing.logger import Logger
log = Logger(__name__)

class _XASessionEvents:
    def __init__(self):
        self.code = -1
        self.msg = None

    def reset(self):
        self.code = -1
        self.msg = None

    def OnLogin(self, code, msg):
        self.code = str(code)
        self.msg = str(msg)

    def OnLogout(self):
        print("OnLogout method is called")

    def OnDisconnect(self):
        print("OnDisconnect method is called")

class Session:
    """세션 관리를 XASession 확장 클래스

        ::

            session = Session()
    """
    def __init__(self):
        self.session = win32com.client.DispatchWithEvents("XA_Session.XASession", _XASessionEvents)

    def login(self, server, user):
        """서버 연결을 요청한다

            :param server: 서버 정보
            :type server: object {address:"서버주소", port:서버포트, type: 서버타입}
            :param user: 사용자 정보
            :type user: object {id:"아이디", passwd:"비밀번호", account_passwd:"계좌비밀번호", certificate_passwd:"공인인증서비밀번호"}
            :return: 로그인이 성공하면 True, 실패하면 Fasle
            :rtype: bool

            ::

                server = {
                    "address" :"hts.ebestsec.co.kr",    # 서버주소
                    "port" : 20001, # 서버포트
                    "type" : 0  # 서버 타입
                }
                user = {
                    "id" : "sculove",   # 아이디
                    "passwd" : "12345678",  # 비밀번호
                    "account_passwd" : "1234",  # 계좌 비밀번호
                    "certificate_passwd" : "12345678"   # 공인인증서 비밀번호
                }
                session = Session()
                session.login(server, user)
        """
        self.session.reset()
        self.session.ConnectServer(server["address"], server["port"])
        self.session.Login(user["id"], user["passwd"], user["certificate_passwd"], server["type"], 0)
        while self.session.code == -1:
            pythoncom.PumpWaitingMessages()
            time.sleep(0.1)

        if self.session.code == "0000":
            log.info("로그인 성공")
            return True
        else:
            log.critical("로그인 실패 : %s" % xacom.parseErrorCode(self.session.code))
            return False

    def logout(self):
        """서버와의 연결을 끊는다.

            ::

                session.logout()
        """
        self.session.DisconnectServer()

    def account(self):
        """계좌 정보를 반환한다.

            :return: 계좌 정보를 반환한다.
            :rtype: object {no:"계좌번호",name:"계좌이름",detailName:"계좌상세이름"}

            ::

                session.account()
        """
        acc = []
        for p in range(self.session.GetAccountListCount()):
            acc.append({
                "no" : self.session.GetAccountList(p),
                "name" : self.session.GetAccountName(p),
                "detailName" : self.session.GetAcctDetailName(p)
            })
        return acc

    def heartbeat(self):
        """서버에 시간을 조회해서 서버 연결여부를 확인한다.

        :return: 연결될 경우, time과 dt를 포함한 dictionary를 반환한다. 연결이 끊어졌을 경우, None을 반환한다
        :rtype: None, object

            - 서버와의 연결이 끊어졌으면 None
            - 서버와의 연결이 유효하면 { time:"mmhhss", dt:"yyyymmdd"}

        ::

            session.heartbeat()
        """
        result = Query("t0167").request(input=None, output={
            "OutBlock" : ("dt","time")
        })
        if result:
            return {
                "time" : result["OutBlock"]["time"][:6],
                "dt" : result["OutBlock"]["dt"]
            }
        else:
            return None