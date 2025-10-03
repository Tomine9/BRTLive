from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.dependencies import get_db, require_admin
from app.schemas.terminal import TerminalCreate, TerminalUpdate, TerminalResponse
from app.models.terminal import Terminal

terminals_router = APIRouter(prefix="/terminals", tags=["Terminals"])

@terminals_router.get("/", response_model=List[TerminalResponse])
async def get_terminals(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all terminals (public - no login needed)"""
    query = select(Terminal).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@terminals_router.get("/{terminal_id}", response_model=TerminalResponse)
async def get_terminal(
    terminal_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get one terminal"""
    result = await db.execute(select(Terminal).filter(Terminal.id == terminal_id))
    terminal = result.scalar_one_or_none()
    
    if not terminal:
        raise HTTPException(status_code=404, detail="Terminal not found")
    
    return terminal

@terminals_router.post("/", response_model=TerminalResponse, status_code=status.HTTP_201_CREATED)
async def create_terminal(
    terminal_data: TerminalCreate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Create new terminal (admin only)"""
    new_terminal = Terminal(**terminal_data.dict())
    db.add(new_terminal)
    await db.commit()
    await db.refresh(new_terminal)
    
    return new_terminal

@terminals_router.put("/{terminal_id}", response_model=TerminalResponse)
async def update_terminal(
    terminal_id: int,
    terminal_data: TerminalUpdate,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Update terminal (admin only)"""
    result = await db.execute(select(Terminal).filter(Terminal.id == terminal_id))
    terminal = result.scalar_one_or_none()
    
    if not terminal:
        raise HTTPException(status_code=404, detail="Terminal not found")
    
    # Update fields
    for field, value in terminal_data.dict(exclude_unset=True).items():
        setattr(terminal, field, value)
    
    await db.commit()
    await db.refresh(terminal)
    
    return terminal

@terminals_router.delete("/{terminal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_terminal(
    terminal_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin)
):
    """Delete terminal (admin only)"""
    result = await db.execute(select(Terminal).filter(Terminal.id == terminal_id))
    terminal = result.scalar_one_or_none()
    
    if not terminal:
        raise HTTPException(status_code=404, detail="Terminal not found")
    
    await db.delete(terminal)
    await db.commit()