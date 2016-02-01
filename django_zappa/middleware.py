import base58
import json

REDIRECT_HTML = """<!DOCTYPE HTML>
<html lang="en-US">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="1;url=REDIRECT_ME">
        <script type="text/javascript">
            window.location.href = "REDIRECT_ME"
        </script>
        <title>Page Redirection</title>
    </head>
    <body>
        <!-- Note: don't tell people to `click` the link, just tell them that it is a link. -->
        If you are not redirected automatically, follow the <a href='REDIRECT_ME'>link to example</a>
    </body>
</html>"""

class ZappaMiddleware(object):

    def process_request(self, request):
        """
        If we have a ZappaCookie, decode it.

        """

        if 'zappa' in request.COOKIES.keys():

            encoded = request.COOKIES['zappa']
            decoded = base58.b58decode(encoded)
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

        # If setting cookie on a 301/2,
        # return 200 and replace the content with a javascript redirector
        if response.status_code != 200 and response.has_header('Location'):
            location = response.get('Location')
            response.content = REDIRECT_HTML.replace('REDIRECT_ME', location)
            response.status_code = 200

        pack = {}
        for key in response.cookies.keys():
            pack[key] = response.cookies[key].value
            del(response.cookies[key])

        pack_s = json.dumps(pack)
        encoded = base58.b58encode(pack_s)

        response.set_cookie('zappa', encoded)

        return response