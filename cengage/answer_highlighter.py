from burp import IBurpExtender, IHttpListener
import json
import zlib

class BurpExtender(IBurpExtender, IHttpListener):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("Learnosity Answer Highlighter")
        callbacks.registerHttpListener(self)
        print("Learnosity Answer Highlighter loaded")

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        httpService = messageInfo.getHttpService()
        if httpService is None:
            return

        host = httpService.getHost()
        if not host or "learnosity.com" not in host.lower():
            return

        requestInfo = self._helpers.analyzeRequest(messageInfo)
        url = requestInfo.getUrl().toString()
        if "/activity" not in url:
            return

        if messageIsRequest:
            self._rewriteRequestEncodings(messageInfo, requestInfo)
            return

        response = messageInfo.getResponse()
        if response is None:
            return

        responseInfo = self._helpers.analyzeResponse(response)
        headers = list(responseInfo.getHeaders())
        body = response[responseInfo.getBodyOffset():]

        encoding = None
        for h in headers:
            hl = h.lower()
            if hl.startswith("content-encoding:"):
                encoding = hl.split(":", 1)[1].strip()
                break

        try:
            if encoding == "gzip":
                body = zlib.decompress(body, 16 + zlib.MAX_WBITS)
            elif encoding == "deflate":
                body = zlib.decompress(body)
        except Exception as e:
            print("decompress error: " + str(e))
            return

        try:
            bodyStr = self._helpers.bytesToString(body)
            data = json.loads(bodyStr)
        except Exception:
            return

        modified = self._highlightTree(data)
        if not modified:
            return

        newBodyStr = json.dumps(data)
        newBody = self._helpers.stringToBytes(newBodyStr)

        newHeaders = []
        for h in headers:
            hl = h.lower()
            if hl.startswith("content-encoding:"):
                continue
            if hl.startswith("content-length:"):
                continue
            newHeaders.append(h)

        newHeaders.append("Content-Length: " + str(len(newBody)))

        newResponse = self._callbacks.getHelpers().buildHttpMessage(newHeaders, newBody)
        messageInfo.setResponse(newResponse)

    def _rewriteRequestEncodings(self, messageInfo, requestInfo):
        request = messageInfo.getRequest()
        headers = list(requestInfo.getHeaders())
        body = request[requestInfo.getBodyOffset():]

        newHeaders = []
        for h in headers:
            if h.lower().startswith("accept-encoding:"):
                newHeaders.append("Accept-Encoding: identity")
            else:
                newHeaders.append(h)

        newRequest = self._helpers.buildHttpMessage(newHeaders, body)
        messageInfo.setRequest(newRequest)

    def _highlightTree(self, node):
        modified = False
        if isinstance(node, dict):
            if self._looksLikeQuestion(node):
                if self._highlightQuestion(node):
                    modified = True
            for v in node.values():
                if self._highlightTree(v):
                    modified = True
        elif isinstance(node, list):
            for item in node:
                if self._highlightTree(item):
                    modified = True
        return modified

    def _looksLikeQuestion(self, obj):
        if "options" not in obj or "validation" not in obj:
            return False

        validation = obj.get("validation") or {}
        vr = validation.get("valid_response") or {}

        if "value" not in vr:
            return False

        if not isinstance(obj.get("options"), list):
            return False
        return True

    def _highlightQuestion(self, q):
        validation = q.get("validation") or {}
        vr = validation.get("valid_response") or {}
        value = vr.get("value")
        if value is None:
            return False

        if isinstance(value, list):
            correctValues = set(str(v) for v in value)
        else:
            correctValues = set([str(value)])

        if not correctValues:
            return False

        options = q.get("options") or []
        changed = False

        for opt in options:
            v = str(opt.get("value", ""))
            if v in correctValues:
                label = opt.get("label", "")

                if not label:
                    continue

                if "<span" in label:
                    continue

                opt["label"] = '<span style="background-color:#ffff00; color:#008000; font-weight:bold;">' + label + '</span>'
                changed = True
        return changed
