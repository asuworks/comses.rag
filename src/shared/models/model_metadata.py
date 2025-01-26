from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ProgrammingLanguage:
    name: str = field(
        metadata={"desc": "Name of the programming language used in the model"}
    )

@dataclass
class Organization:
    type: str = field(
        default="Organization",
        metadata={"desc": "Type of the organization, default is 'Organization'"}
    )
    id: Optional[str] = field(
        default=None,
        metadata={"desc": "Unique identifier for the organization"}
    )
    name: str = field(
        default="",
        metadata={"desc": "Name of the organization"}
    )
    url: Optional[str] = field(
        default=None,
        metadata={"desc": "URL of the organization's website"}
    )
    identifier: Optional[str] = field(
        default=None,
        metadata={"desc": "External identifier for the organization"}
    )
    sameAs: Optional[str] = field(
        default=None,
        metadata={"desc": "URL of a reference page that unambiguously indicates the organization's identity"}
    )

@dataclass
class Person:
    givenName: str = field(
        metadata={"desc": "First name of the person"}
    )
    familyName: str = field(
        metadata={"desc": "Last name of the person"}
    )
    id: str = field(
        metadata={"desc": "Unique identifier for the person"}
    )
    affiliation: Organization = field(
        metadata={"desc": "Organization the person is affiliated with"}
    )
    email: str = field(
        metadata={"desc": "Email address of the person"}
    )

@dataclass
class Tag:
    id: str = field(
        metadata={"desc": "Unique identifier for the tag"}
    )
    name: str = field(
        metadata={"desc": "Name of the tag"}
    )
    description: Optional[str] = field(
        default=None,
        metadata={"desc": "Description of the tag"}
    )
    created_at: str = field(
        default=None,
        metadata={"desc": "Timestamp when the tag was created"}
    )
    updated_at: str = field(
        default=None,
        metadata={"desc": "Timestamp when the tag was last updated"}
    )

@dataclass
class Category:
    id: str = field(
        metadata={"desc": "Unique identifier for the category"}
    )
    name: str = field(
        metadata={"desc": "Name of the category"}
    )
    description: Optional[str] = field(
        default=None,
        metadata={"desc": "Description of the category"}
    )
    parent_id: Optional[str] = field(
        default=None,
        metadata={"desc": "Identifier of the parent category, if any"}
    )
    created_at: str = field(
        default=None,
        metadata={"desc": "Timestamp when the category was created"}
    )
    updated_at: str = field(
        default=None,
        metadata={"desc": "Timestamp when the category was last updated"}
    )

@dataclass
class ModelMetadata:
    id:str = field(
        metadata={"desc": "Unique identifier for the agent based model"}
    )
    name: Optional[str] = field(
        default=None, metadata={"desc": "Name of the agent based model"}
    )
    abstract: Optional[str] = field(
        default=None, metadata={"desc": "Brief summary of the model's purpose and capabilities"}
    )
    description: Optional[str] = field(
        default=None, metadata={"desc": "Detailed description of the agent based model"}
    )
    version: Optional[str] = field(
        default=None, metadata={"desc": "Version number or identifier of the model release"}
    )
    programming_languages: Optional[List[ProgrammingLanguage]] = field(
        default=None, metadata={"desc": "Programming languages used in implementing the model"}
    )
    authors: Optional[List[Person]] = field(
        default=None, metadata={"desc": "List of individuals who contributed to the model's development"}
    )
    url: Optional[str] = field(
        default=None, metadata={"desc": "Web address where the model can be accessed or downloaded"}
    )
    identifier: Optional[str] = field(
        default=None, metadata={"desc": "External reference identifier for the model"}
    )
    date_created: Optional[str] = field(
        default=None, metadata={"desc": "Original creation date of the model"}
    )
    date_modified: Optional[str] = field(
        default=None, metadata={"desc": "Last modification date of the model"}
    )
    keywords: Optional[str] = field(
        default=None, metadata={"desc": "Key terms and phrases associated with the model's domain and functionality"}
    )
    citation: Optional[str] = field(
        default=None, metadata={"desc": "Academic citation or reference for citing the model in publications"}
    )
    license: Optional[str] = field(
        default=None, metadata={"desc": "License terms and conditions for model usage"}
    )
    release_notes: Optional[str] = field(
        default=None, metadata={"desc": "Documentation of changes, improvements, and fixes in this model version"}
    )
    categories: Optional[List[Category]] = field(
        default=None, metadata={"desc": "Classification categories the model belongs to"}
    )
    tags: Optional[List[Tag]] = field(
        default=None, metadata={"desc": "Descriptive tags for model categorization and search"}
    )
    publisher_id: Optional[str] = field(
        default=None, metadata={"desc": "Identifier of the organization or entity publishing the model"}
    )
    created_at: Optional[str] = field(
        default=None, metadata={"desc": "Timestamp when this metadata record was created"}
    )
    updated_at: Optional[str] = field(
        default=None, metadata={"desc": "Timestamp when this metadata record was last updated"}
    )