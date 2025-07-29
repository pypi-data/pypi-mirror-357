# VRoid Web API Python Wrapper

## Example Usage

```python
from sanic import Request, Sanic, json, redirect
from vroid import VRoid, VRoidOAuth

app = Sanic("VRoidApp")


@app.before_server_start
async def setup_vroid_oauth(app: Sanic, _):
    # Initialize VRoidOAuth with your client ID, secret, and redirect URI
    app.ctx.vroid_oauth = await VRoidOAuth.create(
        client_id="your_client_id_here",
        client_secret="your_client_secret_here",
        redirect_uri="http://localhost:8000/redirect",
    )


@app.route("/")
async def redirect_handler(request: Request):
    # Handle the redirect from VRoid OAuth
    url = request.app.ctx.vroid_oauth.request_to_initiate_authorization(
        response_type="code", scope="default"
    )
    return redirect(url)


@app.route("/redirect")
async def handle_redirect(request: Request):
    # Handle the redirect after authorization
    code = request.args.get("code")
    if not code:
        return json({"error": "Authorization code not provided"}, status=400)

    try:
        access_token_response = await request.app.ctx.vroid_oauth.request_access_token(
            code=code, grant_type="authorization_code"
        )
        access_token = access_token_response["access_token"]
        res = json(
            {
                "message": "Access token received successfully",
                "access_token": access_token,
            },
        )
        res.cookies.add_cookie(
            "access_token",
            access_token,
            max_age=3600,
            httponly=True,
        )
        return res
    except Exception as e:
        return json({"error": str(e)}, status=500)


@app.route("/character_models")
async def list_character_models(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return json({"error": "Access token not found"}, status=401)

    async with VRoid(access_token) as vroid:
        try:
            character_models = await vroid.list_of_character_models_posted_by_the_user()
            return json(character_models)
        except Exception as e:
            return json({"error": str(e)}, status=500)


@app.route("/revoke")
async def revoke_access_token(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return json({"error": "Access token not found"}, status=401)

    await app.ctx.vroid_oauth.revoke_access_token(token=access_token)
    return json({"message": "Access token revoked successfully"})
```