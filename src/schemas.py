from __future__ import annotations

from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field


class TestQuality(str, Enum):
    FLEXIBILITY = "Flexibility"
    LOWER_BODY_EXPLOSIVE_STRENGTH = "Lower Body Explosive Strength"
    UPPER_BODY_STRENGTH = "Upper Body Strength"
    SPEED = "Speed"
    AGILITY = "Agility"
    CORE_STRENGTH = "Core Strength"
    ENDURANCE = "Endurance"


SUPPORTED_QUALITIES = [q.value for q in TestQuality]


class RatingRequest(BaseModel):
    """Metadata for the rating request."""

    quality: TestQuality = Field(..., description="Quality being tested.")


class RatingResponse(BaseModel):
    """Response payload returned by the rating pipeline."""

    class TestDescriptor(BaseModel):
        testNumber: int
        sequenceLabel: str
        nameOfTest: str
        qualityTested: str
        ageCategory: Optional[str] = None
        score: float = Field(..., ge=0.0, le=10.0, description="Score 0-10.")

    test: TestDescriptor


TEST_METADATA: Dict[TestQuality, Dict[str, str | int | None]] = {
    TestQuality.FLEXIBILITY: {
        "testNumber": 1,
        "sequenceLabel": "Test 1",
        "nameOfTest": "Sit and Reach",
        "qualityTested": "Flexibility",
        "ageCategory": None,
    },
    TestQuality.LOWER_BODY_EXPLOSIVE_STRENGTH: {
        "testNumber": 2,
        "sequenceLabel": "Test 2",
        "nameOfTest": "Standing Vertical Jump",
        "qualityTested": "Lower Body Explosive Strength",
        "ageCategory": None,
    },
    TestQuality.UPPER_BODY_STRENGTH: {
        "testNumber": 4,
        "sequenceLabel": "Test 4",
        "nameOfTest": "Medicine Ball Throw",
        "qualityTested": "Upper Body Strength",
        "ageCategory": None,
    },
    TestQuality.SPEED: {
        "testNumber": 5,
        "sequenceLabel": "Test 5",
        "nameOfTest": "30mts Standing Start",
        "qualityTested": "Speed",
        "ageCategory": None,
    },
    TestQuality.AGILITY: {
        "testNumber": 6,
        "sequenceLabel": "Test 6",
        "nameOfTest": "4 x 10 mts Shuttle Run",
        "qualityTested": "Agility",
        "ageCategory": None,
    },
    TestQuality.CORE_STRENGTH: {
        "testNumber": 7,
        "sequenceLabel": "Test 7",
        "nameOfTest": "Sit Ups",
        "qualityTested": "Core Strength",
        "ageCategory": None,
    },
    TestQuality.ENDURANCE: {
        "testNumber": 8,
        "sequenceLabel": "Test 8",
        "nameOfTest": "800m Run for U-12, 1.6km run for 12+ years",
        "qualityTested": "Endurance",
        "ageCategory": "U-12 / 12+",
    },
}


def get_metadata_for_quality(quality: TestQuality) -> Dict[str, str | int | None]:
    """Return test metadata for the selected quality."""
    return TEST_METADATA[quality]
