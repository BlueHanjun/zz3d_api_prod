from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入各个API路由
from apis.auth import router as auth_router
from apis.user import router as user_router
from apis.keys import router as keys_router
from apis.billing import router as billing_router
from apis.usage import router as usage_router
from openapis.openapi import router as openapi_router

app = FastAPI(title="zz3d API", description="zz3d 后端 API 接口", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册各个API路由
app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(user_router, prefix="/api/user", tags=["用户"])
app.include_router(keys_router, prefix="/api/keys", tags=["API密钥"])
app.include_router(billing_router, prefix="/api/billing", tags=["计费和账单"])
app.include_router(usage_router, prefix="/api/usage", tags=["用量"])
app.include_router(openapi_router, prefix="/api/openapi", tags=["开放API"])


@app.get("/")
async def root():
    return {"message": "欢迎使用 zz3d API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)