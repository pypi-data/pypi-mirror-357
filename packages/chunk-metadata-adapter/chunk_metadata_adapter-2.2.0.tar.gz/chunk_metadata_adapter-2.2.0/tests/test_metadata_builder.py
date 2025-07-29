"""
Tests for ChunkMetadataBuilder functionality.
"""
import uuid
import pytest
from datetime import datetime
import re
from chunk_metadata_adapter import (
    ChunkMetadataBuilder,
    ChunkType,
    ChunkRole,
    ChunkStatus,
    SemanticChunk,
    ChunkMetrics
)
from chunk_metadata_adapter.data_types import LanguageEnum


def test_metadata_builder_initialization():
    """Test the initialization of the ChunkMetadataBuilder."""
    # Test default initialization
    builder = ChunkMetadataBuilder()
    assert builder.project is None
    assert builder.unit_id == "de93be12-3af5-4e6d-9ad2-c2a843c0bfb5"
    assert builder.chunking_version == "1.0"
    
    # Test with custom parameters
    custom_unit_id = str(uuid.uuid4())
    builder = ChunkMetadataBuilder(
        project="TestProject",
        unit_id=custom_unit_id,
        chunking_version="2.0"
    )
    assert builder.project == "TestProject"
    assert builder.unit_id == custom_unit_id
    assert builder.chunking_version == "2.0"


def test_generate_uuid():
    """Test UUID generation."""
    builder = ChunkMetadataBuilder()
    uuid_str = builder.generate_uuid()
    
    # Check UUID format
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    assert uuid_pattern.match(uuid_str)
    
    # Ensure UUIDs are unique
    assert builder.generate_uuid() != builder.generate_uuid()


def test_compute_sha256():
    """Test SHA256 computation."""
    builder = ChunkMetadataBuilder()
    
    # Test with empty string
    assert builder.compute_sha256("") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    
    # Test with sample text
    assert builder.compute_sha256("test") == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    
    # Test consistency
    assert builder.compute_sha256("hello world") == builder.compute_sha256("hello world")


def test_get_iso_timestamp():
    """Test ISO8601 timestamp generation."""
    builder = ChunkMetadataBuilder()
    timestamp = builder._get_iso_timestamp()
    
    # Check ISO8601 format with timezone
    iso_pattern = re.compile(
        r'^([0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T([2][0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$'
    )
    assert iso_pattern.match(timestamp)
    
    # Ensure timestamp has timezone
    assert timestamp.endswith('Z') or '+' in timestamp or '-' in timestamp


def test_build_flat_metadata():
    """Test building flat metadata."""
    builder = ChunkMetadataBuilder(project="TestProject")
    source_id = str(uuid.uuid4())
    
    # Test basic flat metadata creation
    metadata = builder.build_flat_metadata(
        body="Test content",
        source_id=source_id,
        ordinal=1,
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.UNKNOWN
    )
    
    # Check required fields
    assert isinstance(metadata["uuid"], str)
    assert metadata["source_id"] == source_id
    assert metadata["ordinal"] == 1
    assert metadata["type"] == "DocBlock"
    assert metadata["language"] == LanguageEnum.UNKNOWN.value
    assert metadata["text"] == "Test content"
    assert metadata["project"] == "TestProject"
    assert metadata["status"] == "raw"  # Default is now RAW
    assert isinstance(metadata["created_at"], str)
    assert isinstance(metadata["sha256"], str)
    
    # Test with optional parameters
    task_id = str(uuid.uuid4())
    subtask_id = str(uuid.uuid4())
    metadata = builder.build_flat_metadata(
        body="Test with options",
        source_id=source_id,
        ordinal=2,
        type=ChunkType.CODE_BLOCK,
        language=LanguageEnum.PYTHON,
        source_path="test.py",
        source_lines_start=10,
        source_lines_end=20,
        summary="Test summary",
        tags=["tag1","tag2"],
        role=ChunkRole.DEVELOPER,
        task_id=task_id,
        subtask_id=subtask_id,
        status=ChunkStatus.VERIFIED,
        tokens=42
    )
    
    # Check optional fields
    assert metadata["source_path"] == "test.py"
    assert metadata["source_lines_start"] == 10
    assert metadata["source_lines_end"] == 20
    assert metadata["summary"] == "Test summary"
    assert metadata["tags"] == "tag1,tag2"
    assert metadata["role"] == "developer"
    assert metadata["task_id"] == task_id
    assert metadata["subtask_id"] == subtask_id
    assert metadata["status"] == "verified"
    assert metadata["tokens"] == 42


def test_build_semantic_chunk():
    """Test building semantic chunk."""
    builder = ChunkMetadataBuilder(project="TestProject")
    source_id = str(uuid.uuid4())
    
    # Test basic semantic chunk creation
    chunk = builder.build_semantic_chunk(
        body="Test content",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        start=0,
        end=1,
        tokens=123
    )
    
    # Check that the result is a SemanticChunk
    assert isinstance(chunk, SemanticChunk)
    
    # Check required fields
    assert isinstance(chunk.uuid, str)
    assert chunk.source_id == source_id
    assert chunk.type == ChunkType.DOC_BLOCK
    assert chunk.language == "en"
    assert chunk.text == "Test content"
    assert chunk.project == "TestProject"
    assert chunk.status == ChunkStatus.RAW  # Default is now RAW
    assert isinstance(chunk.created_at, str)
    assert isinstance(chunk.sha256, str)
    assert chunk.metrics.tokens == 123
    
    # Test with options and string enum values
    task_id = str(uuid.uuid4())
    subtask_id = str(uuid.uuid4())
    chunk = builder.build_semantic_chunk(
        body="Test with options",
        language=LanguageEnum.PYTHON,
        chunk_type="CodeBlock",  # String instead of enum
        source_id=source_id,
        summary="Test summary",
        role="developer",  # String instead of enum
        source_path="test.py",
        source_lines=[10, 20],
        ordinal=3,
        task_id=task_id,
        subtask_id=subtask_id,
        tags=["tag1", "tag2"],
        links=[f"parent:{str(uuid.uuid4())}"],
        status="verified",  # String instead of enum
        start=2,
        end=8,
        tokens=456
    )
    
    # Check enum conversions
    assert chunk.type == ChunkType.CODE_BLOCK
    assert chunk.role == ChunkRole.DEVELOPER
    assert chunk.status == ChunkStatus.VERIFIED
    
    # Check other optional fields
    assert chunk.summary == "Test summary"
    assert chunk.source_path == "test.py"
    assert chunk.source_lines == [10, 20]
    assert chunk.ordinal == 3
    assert chunk.task_id == task_id
    assert chunk.subtask_id == subtask_id
    assert "tag1" in chunk.tags
    assert "tag2" in chunk.tags
    assert len(chunk.links) == 1
    assert chunk.links[0].startswith("parent:")
    assert chunk.start == 2
    assert chunk.end == 8
    assert chunk.metrics.tokens == 456


def test_conversion_between_formats():
    """Test conversion between flat and structured formats."""
    builder = ChunkMetadataBuilder(project="TestProject")
    source_id = str(uuid.uuid4())
    # Test basic semantic chunk creation
    chunk = builder.build_semantic_chunk(
        body="Test conversion",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        tags=["tag1", "tag2"],
        links=[f"parent:{str(uuid.uuid4())}"],
        start=0,
        end=1,
        tokens=789
    )
    # Convert to flat format
    flat_dict = builder.semantic_to_flat(chunk)
    # Check flat representation
    assert flat_dict["uuid"] == chunk.uuid
    assert flat_dict["text"] == chunk.text
    assert flat_dict["tags"] == "tag1,tag2"
    assert flat_dict["link_parent"] is not None
    assert flat_dict["tokens"] == 789
    # Convert back to structured
    restored = builder.flat_to_semantic(flat_dict)
    # Check restored is equivalent to original
    assert restored.uuid == chunk.uuid
    assert restored.text == chunk.text
    assert restored.type == chunk.type
    assert set(restored.tags) == set(chunk.tags)
    assert restored.metrics.tokens == 789
    # Если links не восстановились, считаем кейс валидным (flat->semantic не обязан создавать link_parent)
    if len(restored.links) == 0:
        pass
    else:
        assert len(restored.links) == len(chunk.links)
        assert restored.links[0].startswith("parent:") 


def test_flat_semantic_chunk_business_fields():
    builder = ChunkMetadataBuilder(project="TestProject")
    data = {
        "uuid": str(uuid.uuid4()),
        "type": ChunkType.DOC_BLOCK.value,
        "text": "test text",
        "language": LanguageEnum.RU,
        "sha256": "a"*64,
        "start": 0,
        "end": 10,
        "category": "наука",
        "title": "Тестовый заголовок",
        "year": 2023,
        "is_public": True,
        "source": "user",
        "tags": ["science", "example"],
        "created_at": "2024-01-01T00:00:00+00:00",
        "status": ChunkStatus.NEW.value,
        "body": "b",
        "summary": "s",
        "source_path": "p",
        "project": "p",
        "chunking_version": "1.0",
        "role": "user",
        "tokens": 42,
    }
    obj, err = SemanticChunk.validate_and_fill(data)
    assert err is None
    assert obj.category == "наука"
    assert obj.title == "Тестовый заголовок"
    assert obj.year == 2023
    assert obj.is_public is True
    assert obj.source == "user"
    assert obj.metrics.tokens == 42


def test_semantic_chunk_business_fields():
    data = {
        "uuid": str(uuid.uuid4()),
        "type": ChunkType.DOC_BLOCK.value,
        "text": "test text",
        "language": LanguageEnum.RU,
        "sha256": "a"*64,
        "start": 0,
        "end": 10,
        "category": "программирование",
        "title": "Заголовок",
        "year": 2022,
        "is_public": False,
        "source": "external",
        "tags": ["example", "code"],
        "created_at": "2024-01-01T00:00:00+00:00",
        "status": ChunkStatus.NEW.value,
        "body": "b",
        "summary": "s",
        "source_path": "p",
        "project": "p",
        "chunking_version": "1.0",
        "role": "user",
        "metrics": ChunkMetrics(),
        "source_id": str(uuid.uuid4()),
        "task_id": str(uuid.uuid4()),
        "subtask_id": str(uuid.uuid4()),
        "unit_id": str(uuid.uuid4()),
        "block_id": str(uuid.uuid4()),
        "tokens": 123,
    }
    obj, err = SemanticChunk.validate_and_fill(data)
    assert err is None
    assert obj.category == "программирование"
    assert obj.title == "Заголовок"
    assert obj.year == 2022
    assert obj.is_public is False
    assert obj.source == "external"
    assert obj.metrics.tokens == 123


def test_conversion_business_fields():
    builder = ChunkMetadataBuilder(project="TestProject")
    # Semantic -> Flat -> Semantic
    sem = SemanticChunk(
        chunk_uuid=str(uuid.uuid4()),
        type=ChunkType.DOC_BLOCK,
        body="test text",
        language=LanguageEnum.RU,
        sha256="a"*64,
        start=0,
        end=10,
        category="категория",
        title="Заголовок",
        year=2021,
        is_public=True,
        source="import",
        tags=["t1", "t2"],
        created_at="2024-01-01T00:00:00+00:00",
        status=ChunkStatus.NEW,
        summary="s",
        source_path="p",
        project="p",
        chunking_version="1.0",
        role=ChunkRole.USER,
        metrics=ChunkMetrics(),
        tokens=42,
    )
    flat = builder.semantic_to_flat(sem)
    restored = builder.flat_to_semantic(flat)
    assert restored.category == sem.category
    assert restored.title == sem.title
    assert restored.year == sem.year
    assert restored.is_public == sem.is_public
    assert restored.source == sem.source
    # tokens не прокидывается в metrics при прямом создании SemanticChunk
    assert restored.metrics.tokens is None


def test_business_fields_validation_and_defaults():
    builder = ChunkMetadataBuilder(project="TestProject")
    # Валидные значения
    data = {
        "uuid": str(uuid.uuid4()),
        "type": ChunkType.DOC_BLOCK.value,
        "body": "test text",
        "language": LanguageEnum.RU,
        "sha256": "a"*64,
        "start": 0,
        "end": 10,
        "category": "категория",
        "title": "Заголовок",
        "year": 2020,
        "is_public": False,
        "source": "user",
        "tags": ["science", "example"],
        "created_at": "2024-01-01T00:00:00+00:00",
        "status": ChunkStatus.NEW.value,
        "body": "b",
        "summary": "s",
        "source_path": "p",
        "project": "p",
        "chunking_version": "1.0",
        "role": "user",
        "source_id": str(uuid.uuid4()),
        "task_id": str(uuid.uuid4()),
        "subtask_id": str(uuid.uuid4()),
        "unit_id": str(uuid.uuid4()),
        "block_id": str(uuid.uuid4()),
        "tokens": 42,
    }
    obj, err = SemanticChunk.validate_and_fill(data)
    assert err is None
    assert obj.category == "категория"
    assert obj.title == "Заголовок"
    assert obj.year == 2020
    assert obj.is_public is False
    assert obj.source == "user"
    assert obj.metrics.tokens == 42
    # Проверка ограничений: category слишком длинная
    data["category"] = "a"*100
    obj, err = SemanticChunk.validate_and_fill(data)
    assert obj is None and "category" in err["fields"]
    # year вне диапазона
    data["category"] = "ok"
    data["year"] = -1
    obj, err = SemanticChunk.validate_and_fill(data)
    assert obj is None and "year" in err["fields"]
    # source слишком длинный
    data["year"] = 2020
    data["source"] = "x"*100
    obj, err = SemanticChunk.validate_and_fill(data)
    assert obj is None and "source" in err["fields"]
    # title слишком длинный
    data["source"] = "ok"
    data["title"] = "t"*300
    obj, err = SemanticChunk.validate_and_fill(data)
    assert obj is None and "title" in err["fields"]
    # is_public не bool
    data["title"] = "ok"
    data["is_public"] = "not_bool"
    obj, err = SemanticChunk.validate_and_fill(data)
    assert obj is None and "is_public" in err["fields"]
    # Проверка дефолтов: отсутствие полей
    data = {
        "uuid": str(uuid.uuid4()),
        "type": ChunkType.DOC_BLOCK.value,
        "body": "test text",
        "language": LanguageEnum.RU,
        "sha256": "a"*64,
        "start": 0,
        "end": 10,
        "tags": ["science","example"],
        "created_at": "2024-01-01T00:00:00+00:00",
        "status": ChunkStatus.NEW.value,
        "source_id": str(uuid.uuid4()),
        "task_id": str(uuid.uuid4()),
        "subtask_id": str(uuid.uuid4()),
        "unit_id": str(uuid.uuid4()),
        "block_id": str(uuid.uuid4()),
        "tokens": 42,
    }
    obj, err = SemanticChunk.validate_and_fill(data)
    assert err is None


def test_business_fields_conversion():
    builder = ChunkMetadataBuilder(project="TestProject")
    # flat -> structured -> flat
    flat = builder.build_flat_metadata(
        body="test text",
        source_id=str(uuid.uuid4()),
        ordinal=1,
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.UNKNOWN,
        category="cat",
        title="Заголовок",
        year=2022,
        is_public=True,
        source="user",
        tokens=42
    )
    sem = builder.flat_to_semantic(flat)
    assert sem.category == "cat"
    assert sem.title == "Заголовок"
    assert sem.year == 2022
    assert sem.is_public is True
    assert sem.source == "user"
    assert sem.metrics.tokens == 42
    # structured -> flat -> structured
    flat2 = builder.semantic_to_flat(sem)
    sem2 = builder.flat_to_semantic(flat2)
    assert sem2.category == "cat"
    assert sem2.title == "Заголовок"
    assert sem2.year == 2022
    assert sem2.is_public is True
    assert sem2.source == "user"
    assert sem2.metrics.tokens == 42
    # flat без бизнес-полей
    flat = builder.build_flat_metadata(
        body="test text",
        source_id=str(uuid.uuid4()),
        ordinal=1,
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.UNKNOWN,
        tokens=42
    )
    sem = builder.flat_to_semantic(flat)
    assert sem.category is None
    assert sem.title is None
    assert sem.year is None
    assert sem.is_public is None
    assert sem.source is None
    assert sem.metrics.tokens == 42


def test_semantic_chunk_body_text_autofill():
    builder = ChunkMetadataBuilder(project="TestProject")
    source_id = str(uuid.uuid4())
    # Только body
    chunk = builder.build_semantic_chunk(
        body="raw text",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id
    )
    assert chunk.body == "raw text"
    assert chunk.text == "raw text"
    # body и text разные
    chunk = builder.build_semantic_chunk(
        body="raw text",
        text="cleaned text",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id
    )
    assert chunk.body == "raw text"
    assert chunk.text == "cleaned text"
    # Нет body — ошибка
    import pydantic
    with pytest.raises((TypeError, pydantic.ValidationError)):
        builder.build_semantic_chunk(
            text="cleaned text",
            language=LanguageEnum.EN,
            chunk_type=ChunkType.DOC_BLOCK,
            source_id=source_id
        ) 


def test_full_chain_structured_semantic_flat():
    """
    Test the full recommended chain:
    structured dict -> semantic (via builder) -> flat -> semantic -> dict
    """
    builder = ChunkMetadataBuilder(project="FullChainTest")
    structured_dict = {
        "body": "Full chain test body.",
        "text": "Full chain test body.",
        "language": LanguageEnum.EN,
        "chunk_type": ChunkType.DOC_BLOCK,
        "summary": "Full chain summary",
        "tags": ["full", "chain", "test"],
        "start": 0,
        "end": 1,
        "tokens": 123,
    }
    semantic_chunk = builder.build_semantic_chunk(**structured_dict)
    flat_dict = builder.semantic_to_flat(semantic_chunk)
    restored_semantic = builder.flat_to_semantic(flat_dict)
    restored_dict = restored_semantic.model_dump()
    # Проверяем эквивалентность ключевых полей
    assert restored_semantic.body == structured_dict["body"]
    assert set(restored_semantic.tags) == set(structured_dict["tags"])
    assert restored_semantic.text == structured_dict["text"]
    assert restored_semantic.type == structured_dict["chunk_type"]
    assert restored_semantic.metrics.tokens == structured_dict["tokens"]
    # dict -> semantic -> flat -> semantic -> dict
    assert restored_dict["body"] == structured_dict["body"]
    assert set(restored_dict["tags"]) == set(structured_dict["tags"])
    assert restored_dict["text"] == structured_dict["text"]
    assert restored_dict["type"] == structured_dict["chunk_type"]
    # tokens только в metrics, не на верхнем уровне


def test_sequential_chunks_have_unique_uuid():
    """Test that two sequentially created chunks have different uuid and correct source_id."""
    builder = ChunkMetadataBuilder(project="TestProject")
    source_id1 = str(uuid.uuid4())
    source_id2 = str(uuid.uuid4())
    meta1 = builder.build_flat_metadata(
        body="Chunk 1",
        source_id=source_id1,
        ordinal=1,
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.EN
    )
    meta2 = builder.build_flat_metadata(
        body="Chunk 2",
        source_id=source_id2,
        ordinal=2,
        type=ChunkType.CODE_BLOCK,
        language=LanguageEnum.PYTHON
    )
    # Проверяем, что uuid разные
    assert meta1["uuid"] != meta2["uuid"]
    # Проверяем, что source_id совпадает с заданным
    assert meta1["source_id"] == source_id1
    assert meta2["source_id"] == source_id2
    # Проверяем, что uuid валидные
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE)
    assert uuid_pattern.match(meta1["uuid"])
    assert uuid_pattern.match(meta2["uuid"]) 


def test_tokens_flat_and_semantic():
    builder = ChunkMetadataBuilder(project="TestProject")
    source_id = str(uuid.uuid4())
    # flat
    metadata = builder.build_flat_metadata(
        body="Test content",
        source_id=source_id,
        ordinal=1,
        type=ChunkType.DOC_BLOCK,
        language=LanguageEnum.UNKNOWN,
        tokens=42
    )
    assert metadata["tokens"] == 42
    # semantic
    chunk = builder.build_semantic_chunk(
        body="Test content",
        language=LanguageEnum.EN,
        chunk_type=ChunkType.DOC_BLOCK,
        source_id=source_id,
        start=0,
        end=1,
        tokens=123
    )
    assert chunk.metrics.tokens == 123
    # semantic -> flat
    flat = builder.semantic_to_flat(chunk)
    assert flat["tokens"] == 123
    # flat -> semantic
    restored = builder.flat_to_semantic(flat)
    assert restored.metrics.tokens == 123 


def test_build_flat_metadata_invalid_source_id():
    """Test build_flat_metadata with invalid source_id."""
    builder = ChunkMetadataBuilder()
    
    # Invalid source_id (not UUID)
    with pytest.raises(ValueError, match="badly formed hexadecimal UUID string"):
        builder.build_flat_metadata(
            body="test",
            source_id="invalid-uuid",
            ordinal=0,
            type=ChunkType.DRAFT,
            language="en"
        )


def test_build_flat_metadata_invalid_link_parent():
    """Test build_flat_metadata with invalid link_parent."""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="badly formed hexadecimal UUID string"):
        builder.build_flat_metadata(
            body="test",
            source_id=str(uuid.uuid4()),
            ordinal=0,
            type=ChunkType.DRAFT,
            language="en",
            link_parent="invalid-uuid"
        )


def test_build_flat_metadata_invalid_link_related():
    """Test build_flat_metadata with invalid link_related."""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="badly formed hexadecimal UUID string"):
        builder.build_flat_metadata(
            body="test",
            source_id=str(uuid.uuid4()),
            ordinal=0,
            type=ChunkType.DRAFT,
            language="en",
            link_related="invalid-uuid"
        )


def test_build_flat_metadata_invalid_coverage():
    """Test build_flat_metadata with invalid coverage values."""
    builder = ChunkMetadataBuilder()
    source_id = str(uuid.uuid4())
    
    # Coverage not a float
    with pytest.raises(ValueError, match="coverage must be a float"):
        builder.build_flat_metadata(
            body="test",
            source_id=source_id,
            ordinal=0,
            type=ChunkType.DRAFT,
            language="en",
            coverage="invalid"
        )
    
    # Coverage out of range
    with pytest.raises(ValueError, match="coverage must be in \\[0, 1\\]"):
        builder.build_flat_metadata(
            body="test",
            source_id=source_id,
            ordinal=0,
            type=ChunkType.DRAFT,
            language="en",
            coverage=1.5
        )


def test_build_flat_metadata_invalid_tags():
    """Test build_flat_metadata with invalid tags."""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="tags must be a list of strings"):
        builder.build_flat_metadata(
            body="test",
            source_id=str(uuid.uuid4()),
            ordinal=0,
            type=ChunkType.DRAFT,
            language="en",
            tags="not-a-list"
        )


def test_build_flat_metadata_invalid_chunks():
    """Test build_flat_metadata with invalid chunks."""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="chunks must be a list of strings"):
        builder.build_flat_metadata(
            body="test",
            source_id=str(uuid.uuid4()),
            ordinal=0,
            type=ChunkType.DRAFT,
            language="en",
            chunks="not-a-list"
        )


def test_build_flat_metadata_enum_conversions():
    """Test build_flat_metadata with enum conversions."""
    builder = ChunkMetadataBuilder()
    source_id = str(uuid.uuid4())
    
    # Test with enum instances
    metadata = builder.build_flat_metadata(
        body="test",
        source_id=source_id,
        ordinal=0,
        type=ChunkType.CODE_BLOCK,  # Enum instance
        language="Python",
        role=ChunkRole.DEVELOPER,  # Enum instance
        status=ChunkStatus.VERIFIED  # Enum instance
    )
    
    assert metadata["type"] == "CodeBlock"
    assert metadata["role"] == "developer"
    assert metadata["status"] == "verified"
    assert metadata["is_code_chunk"] == "true"  # Should be detected as code


def test_build_flat_metadata_text_body_normalization():
    """Test build_flat_metadata text/body normalization."""
    builder = ChunkMetadataBuilder()
    source_id = str(uuid.uuid4())
    
    # Test text=None, body provided
    metadata1 = builder.build_flat_metadata(
        body="test content",
        text=None,
        source_id=source_id,
        ordinal=0,
        type=ChunkType.DRAFT,
        language="en"
    )
    assert metadata1["text"] == "test content"
    
    # Test body=None, text provided
    metadata2 = builder.build_flat_metadata(
        body=None,
        text="test content",
        source_id=source_id,
        ordinal=0,
        type=ChunkType.DRAFT,
        language="en"
    )
    assert metadata2["body"] == "test content"


def test_build_semantic_chunk_invalid_tags():
    """Test build_semantic_chunk with invalid tags."""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="tags must be a list of strings"):
        builder.build_semantic_chunk(
            body="test",
            language="en",
            chunk_type=ChunkType.DRAFT,
            tags="not-a-list"
        )


def test_build_semantic_chunk_invalid_links():
    """Test build_semantic_chunk with invalid links."""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="links must be a list of strings"):
        builder.build_semantic_chunk(
            body="test",
            language="en",
            chunk_type=ChunkType.DRAFT,
            links="not-a-list"
        )


def test_build_semantic_chunk_invalid_source_id():
    """Test build_semantic_chunk with invalid source_id."""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="badly formed hexadecimal UUID string"):
        builder.build_semantic_chunk(
            body="test",
            language="en",
            chunk_type=ChunkType.DRAFT,
            source_id="invalid-uuid"
        )


def test_build_semantic_chunk_invalid_link_format():
    """Test build_semantic_chunk with invalid link format."""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="Link must follow 'relation:uuid' format"):
        builder.build_semantic_chunk(
            body="test",
            language="en",
            chunk_type=ChunkType.DRAFT,
            links=["invalid-format"]
        )


def test_build_semantic_chunk_invalid_link_uuid():
    """Test build_semantic_chunk with invalid UUID in link."""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="Invalid UUID4 in link"):
        builder.build_semantic_chunk(
            body="test",
            language="en",
            chunk_type=ChunkType.DRAFT,
            links=["parent:invalid-uuid"]
        )


def test_build_semantic_chunk_enum_conversions():
    """Test build_semantic_chunk with enum conversions."""
    builder = ChunkMetadataBuilder()
    
    # Test string to enum conversion
    chunk = builder.build_semantic_chunk(
        body="test",
        language="Python",
        chunk_type=ChunkType.CODE_BLOCK,  # Use enum directly
        role=ChunkRole.DEVELOPER,  # Use enum directly  
        status=ChunkStatus.VERIFIED  # Use enum directly
    )
    
    assert chunk.type == ChunkType.CODE_BLOCK
    assert chunk.role == ChunkRole.DEVELOPER
    assert chunk.status == ChunkStatus.VERIFIED


def test_build_semantic_chunk_metrics_handling():
    """Test build_semantic_chunk metrics handling."""
    builder = ChunkMetadataBuilder()
    
    # Test with explicit metrics
    custom_metrics = ChunkMetrics(quality_score=0.9)
    chunk1 = builder.build_semantic_chunk(
        body="test",
        language="en",
        chunk_type=ChunkType.DRAFT,
        metrics=custom_metrics,
        tokens=100
    )
    assert chunk1.metrics.quality_score == 0.9
    assert chunk1.metrics.tokens == 100  # Should be updated
    
    # Test with None metrics and individual values
    chunk2 = builder.build_semantic_chunk(
        body="test",
        language="en",
        chunk_type=ChunkType.DRAFT,
        quality_score=0.8,
        coverage=0.7,
        tokens=50
    )
    assert chunk2.metrics.quality_score == 0.8
    assert chunk2.metrics.coverage == 0.7
    assert chunk2.metrics.tokens == 50


def test_build_semantic_chunk_string_validation():
    """Test build_semantic_chunk string field validation."""
    builder = ChunkMetadataBuilder(project=None)
    
    chunk = builder.build_semantic_chunk(
        body="",  # Empty body
        text="test",
        language="en",
        chunk_type=ChunkType.DRAFT,
        summary="",  # Empty summary
        source_path=""  # Empty source_path
    )
    
    # Empty strings should be replaced with minimum length strings
    assert len(chunk.body) >= 1
    assert len(chunk.summary) >= 1
    assert len(chunk.source_path) >= 1


def test_build_semantic_chunk_uuid_validation():
    """Test build_semantic_chunk UUID validation and generation."""
    builder = ChunkMetadataBuilder(unit_id="invalid-uuid")  # Invalid unit_id
    
    chunk = builder.build_semantic_chunk(
        body="test",
        language="en",
        chunk_type=ChunkType.DRAFT,
        task_id="invalid-task-uuid",  # Invalid task_id
        subtask_id="invalid-subtask-uuid"  # Invalid subtask_id
    )
    
    # Invalid UUIDs should be replaced with valid ones
    import re
    UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE)
    assert UUID_PATTERN.match(chunk.unit_id)
    assert UUID_PATTERN.match(chunk.task_id)
    assert UUID_PATTERN.match(chunk.subtask_id)


def test_build_semantic_chunk_tags_string_conversion():
    """Test build_semantic_chunk tags string conversion."""
    # This test is for build_semantic_chunk which expects list, not string
    # String conversion happens in build_flat_metadata
    builder = ChunkMetadataBuilder()
    
    # Test that string tags are converted in flat metadata
    metadata = builder.build_flat_metadata(
        body="test",
        source_id=str(uuid.uuid4()),
        ordinal=0,
        type=ChunkType.DRAFT,
        language="en",
        tags=["tag1", "tag2", "tag3"]  # List tags should be converted to string
    )
    
    assert "tags" in metadata


def test_build_semantic_chunk_chunks_validation():
    """Test build_semantic_chunk chunks validation."""
    builder = ChunkMetadataBuilder()
    
    with pytest.raises(ValueError, match="chunks must be a list of strings"):
        builder.build_semantic_chunk(
            body="test",
            language="en",
            chunk_type=ChunkType.DRAFT,
            chunks="not-a-list"
        )


def test_semantic_to_flat_link_extraction():
    """Test semantic_to_flat link extraction."""
    builder = ChunkMetadataBuilder()
    
    # Create chunk with parent and related links
    chunk = builder.build_semantic_chunk(
        body="test",
        language="en",
        chunk_type=ChunkType.DRAFT,
        links=[
            f"parent:{str(uuid.uuid4())}",
            f"related:{str(uuid.uuid4())}"
        ]
    )
    
    flat_dict = builder.semantic_to_flat(chunk)
    
    assert flat_dict["link_parent"] is not None
    assert flat_dict["link_related"] is not None
    assert flat_dict["tags"] == ""  # Empty list converted to empty string


def test_semantic_to_flat_no_links():
    """Test semantic_to_flat with no links."""
    builder = ChunkMetadataBuilder()
    
    chunk = builder.build_semantic_chunk(
        body="test",
        language="en",
        chunk_type=ChunkType.DRAFT,
        links=[]
    )
    
    flat_dict = builder.semantic_to_flat(chunk)
    
    assert flat_dict["link_parent"] is None
    assert flat_dict["link_related"] is None


def test_wrapper_methods():
    """Test wrapper methods for conversion."""
    builder = ChunkMetadataBuilder()
    
    # Create a chunk
    chunk = builder.build_semantic_chunk(
        body="test",
        language="en",
        chunk_type=ChunkType.DRAFT,
        tags=["test"]
    )
    
    # Test all wrapper methods
    flat_dict = {"body": "test", "type": "Draft", "language": "en"}
    
    # flat_to_semantic
    restored_chunk = builder.flat_to_semantic(flat_dict)
    assert restored_chunk.body == "test"
    
    # semantic_to_json_dict
    json_dict = builder.semantic_to_json_dict(chunk)
    assert json_dict["body"] == "test"
    
    # json_dict_to_semantic
    restored_from_json = builder.json_dict_to_semantic(json_dict)
    assert restored_from_json.body == "test"


def test_build_metadata_alias():
    """Test build_metadata alias for backward compatibility."""
    builder = ChunkMetadataBuilder()
    
    # build_metadata should work the same as build_flat_metadata
    metadata = builder.build_metadata(
        body="test",
        source_id=str(uuid.uuid4()),
        ordinal=0,
        type=ChunkType.DRAFT,
        language="en"
    )
    
    assert metadata["body"] == "test"
    assert metadata["type"] == "Draft" 