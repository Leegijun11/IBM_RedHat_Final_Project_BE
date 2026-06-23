



@router.post("babies/create", response_model=Baby_Read)
async def routers_babies_create(baby:Baby_Create, db: AsyncSession = Depends(get_db)):
    


