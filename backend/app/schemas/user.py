from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    name: str

    def from_tortoise_orm(cls, obj):
        return cls(
            username=obj.username,
            name=obj.name,
        )

    def from_queryset(cls, queryset):
        return [cls.from_tortoise_orm(obj) for obj in queryset]

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class UserDelete(BaseModel):
    username: str

class UserLogin(BaseModel):
    username: str
    password: str

