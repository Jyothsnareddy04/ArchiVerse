from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    plot_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="projects")
    layouts = relationship("Layout", back_populates="project")
    blueprints = relationship("Blueprint", back_populates="project")
    interiors = relationship("Interior", back_populates="project")
    exteriors = relationship("Exterior", back_populates="project")
    costs = relationship("Cost", back_populates="project")

class Layout(Base):
    __tablename__ = "layouts"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    data = Column(JSON)
    project = relationship("Project", back_populates="layouts")

class Blueprint(Base):
    __tablename__ = "blueprints"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    data = Column(JSON)
    project = relationship("Project", back_populates="blueprints")

class Interior(Base):
    __tablename__ = "interiors"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    data = Column(JSON)
    project = relationship("Project", back_populates="interiors")

class Exterior(Base):
    __tablename__ = "exteriors"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    data = Column(JSON)
    project = relationship("Project", back_populates="exteriors")

class Cost(Base):
    __tablename__ = "costs"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    data = Column(JSON)
    project = relationship("Project", back_populates="costs")
