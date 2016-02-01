import base64
import json

class ZappaMiddleware(object):

    def process_request(self, request):
        """
        If we have a ZappaCookie, decode it.

        """

        if 'zappa' in request.COOKIES.keys():

            encoded = request.COOKIES['zappa']
            decoded = base64.b64decode(encoded)
            parsed = json.loads(decoded)

            request.COOKIES = {}
            request.COOKIES = parsed

        return

    def process_response(self, request, response):
        """
        If we have multiple Set-Cookies, combine them into a single ZappaCookie.
        Returns the modified HTTP Response.

        """

        if not response.cookies.keys():
            return response

        pack = {}
        for key in response.cookies.keys():
            pack[key] = response.cookies[key].value
            del(response.cookies[key])

        pack_s = json.dumps(pack)
        encoded = base64.b64encode(pack_s)

        response.set_cookie('zappa', encoded)

        return response