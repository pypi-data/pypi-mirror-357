"""Obligations tests."""

import pytest

import httpx
from pytest_httpx import HTTPXMock

from kat_bulgaria.kat_api_client import (
    KatApiClient,
    KatError,
    KatErrorType,
    KatErrorSubtype,
    ERR_INVALID_EGN,
    ERR_INVALID_GOV_ID,
    ERR_INVALID_BULSTAT,
    ERR_INVALID_USER_DATA,
    ERR_API_DOWN
)

from .conftest import EGN, GOV_ID, BULSTAT, INVALID_EGN, INVALID_GOV_ID, INVALID_BULSTAT


# region verify_credentials

@pytest.mark.asyncio
async def test_verify_credentials_local_invalid_egn(httpx_mock: HTTPXMock) -> None:
    """Verify credentials - local EGN validation failed."""

    with pytest.raises(KatError) as ctx:
        await KatApiClient().get_obligations_business(INVALID_EGN, GOV_ID, BULSTAT)

    assert len(httpx_mock.get_requests()) == 0
    assert isinstance(ctx.value, KatError)
    assert ctx.value.error_type == KatErrorType.VALIDATION_ERROR
    assert ctx.value.error_subtype == KatErrorSubtype.VALIDATION_EGN_INVALID
    assert ctx.value.error_message == ERR_INVALID_EGN


@pytest.mark.asyncio
async def test_verify_credentials_local_invalid_gov_id_number(httpx_mock: HTTPXMock) -> None:
    """Verify credentials - local government ID number validation failed."""

    with pytest.raises(KatError) as ctx:
        await KatApiClient().get_obligations_business(EGN, INVALID_GOV_ID, BULSTAT)

    assert len(httpx_mock.get_requests()) == 0
    assert isinstance(ctx.value, KatError)
    assert ctx.value.error_type == KatErrorType.VALIDATION_ERROR
    assert ctx.value.error_subtype == KatErrorSubtype.VALIDATION_GOV_ID_NUMBER_INVALID
    assert ctx.value.error_message == ERR_INVALID_GOV_ID


@pytest.mark.asyncio
async def test_verify_credentials_local_invalid_bulstat(httpx_mock: HTTPXMock) -> None:
    """Verify credentials - local Driver License validation failed."""

    with pytest.raises(KatError) as ctx:
        await KatApiClient().get_obligations_business(EGN, GOV_ID, INVALID_BULSTAT)

    assert len(httpx_mock.get_requests()) == 0
    assert isinstance(ctx.value, KatError)
    assert ctx.value.error_type == KatErrorType.VALIDATION_ERROR
    assert ctx.value.error_subtype == KatErrorSubtype.VALIDATION_BULSTAT_INVALID
    assert ctx.value.error_message == ERR_INVALID_BULSTAT


# endregion


# region check_obligations


@pytest.mark.asyncio
async def test_check_obligations_no_fines(
    httpx_mock: HTTPXMock, ok_no_fines: pytest.fixture
) -> None:
    """Check obligations - None."""

    httpx_mock.add_response(json=ok_no_fines)

    resp = await KatApiClient().get_obligations_business(EGN, GOV_ID, BULSTAT)

    assert len(httpx_mock.get_requests()) == 1
    assert len(resp) == 0


@pytest.mark.asyncio
async def test_check_obligations_sample2(
    httpx_mock: HTTPXMock, ok_sample2_6fines: pytest.fixture
) -> None:
    """Check obligations - has served."""

    httpx_mock.add_response(json=ok_sample2_6fines)

    resp = await KatApiClient().get_obligations_business(EGN, GOV_ID, BULSTAT)

    assert len(httpx_mock.get_requests()) == 1
    assert len(resp) == 6
    assert sum(o.is_served for o in resp) == 2
    assert sum(o.amount for o in resp) == 600


@pytest.mark.asyncio
async def test_check_obligations_field_mapping_success(
    httpx_mock: HTTPXMock, ok_fine_served: pytest.fixture
) -> None:
    """Check obligations - verify field mappings is successful."""

    httpx_mock.add_response(json=ok_fine_served)

    resp = await KatApiClient().get_obligations_business(EGN, GOV_ID, BULSTAT)

    assert len(httpx_mock.get_requests()) == 1
    assert len(resp) == 1

    obligation = resp[0]

    assert obligation.unit_group == 1
    assert obligation.status == 0
    assert obligation.amount == 100
    assert obligation.discount_amount == 70
    assert obligation.discount_percentage == 30
    assert obligation.description == "ЕЛ.ФИШ СЕРИЯ K 0000000 29.03.2024"
    assert obligation.is_served is True
    assert obligation.vehicle_number == "PB 0000 АА"
    assert obligation.date_breach == "2024-01-25"
    assert obligation.date_issued == "2024-03-29"
    assert obligation.document_series == "K"
    assert obligation.document_number == "123456"
    assert obligation.breach_of_order == "чл. 21, ал. 1, от ЗДвП"


@pytest.mark.asyncio
async def test_check_obligations_has_served(
    httpx_mock: HTTPXMock, ok_fine_served: pytest.fixture
) -> None:
    """Check obligations - has served."""

    httpx_mock.add_response(json=ok_fine_served)

    resp = await KatApiClient().get_obligations_business(EGN, GOV_ID, BULSTAT)

    assert len(httpx_mock.get_requests()) == 1
    assert len(resp) == 1
    assert resp[0].is_served is True


@pytest.mark.asyncio
async def test_check_obligations_has_not_served(
    httpx_mock: HTTPXMock, ok_fine_not_served: pytest.fixture
) -> None:
    """Check obligations - has NOT served."""

    httpx_mock.add_response(json=ok_fine_not_served)

    resp = await KatApiClient().get_obligations_business(EGN, GOV_ID, BULSTAT)

    assert len(httpx_mock.get_requests()) == 1
    assert len(resp) == 1
    assert resp[0].is_served is False


@pytest.mark.asyncio
async def test_check_obligations_invalid_user_data_sent(
        httpx_mock: HTTPXMock, err_nodatafound: pytest.fixture
) -> None:
    """Check obligations - local EGN validation failed."""

    httpx_mock.add_response(json=err_nodatafound)

    with pytest.raises(KatError) as ctx:
        await KatApiClient().get_obligations_business(EGN, GOV_ID, BULSTAT)

    assert len(httpx_mock.get_requests()) == 1
    assert isinstance(ctx.value, KatError)
    assert ctx.value.error_type == KatErrorType.VALIDATION_ERROR
    assert ctx.value.error_subtype == KatErrorSubtype.VALIDATION_USER_NOT_FOUND_ONLINE
    assert ctx.value.error_message == ERR_INVALID_USER_DATA


@pytest.mark.asyncio
async def test_check_obligations_api_timeout(httpx_mock: HTTPXMock) -> None:
    """Check obligations - remote KAT API timeout."""

    httpx_mock.add_exception(httpx.TimeoutException(""))

    with pytest.raises(KatError) as ctx:
        await KatApiClient().get_obligations_business(EGN, GOV_ID, BULSTAT)

    assert len(httpx_mock.get_requests()) == 1
    assert isinstance(ctx.value, KatError)
    assert ctx.value.error_type == KatErrorType.API_ERROR
    assert ctx.value.error_subtype == KatErrorSubtype.API_TIMEOUT
    assert "request timed out for" in ctx.value.error_message


@pytest.mark.asyncio
async def test_check_obligations_api_down(
    httpx_mock: HTTPXMock, err_apidown: pytest.fixture
) -> None:
    """Check obligations - remote KAT API returns reading error."""

    httpx_mock.add_response(json=err_apidown, status_code=200)

    with pytest.raises(KatError) as ctx:
        await KatApiClient().get_obligations_business(EGN, GOV_ID, BULSTAT)

    assert len(httpx_mock.get_requests()) == 1
    assert isinstance(ctx.value, KatError)
    assert ctx.value.error_type == KatErrorType.API_ERROR
    assert ctx.value.error_subtype == KatErrorSubtype.API_ERROR_READING_DATA
    assert ctx.value.error_message == ERR_API_DOWN


@pytest.mark.asyncio
async def test_check_obligations_non_success_status_code(
    httpx_mock: HTTPXMock, ok_no_fines: pytest.fixture
) -> None:
    """Check obligations - remote KAT API returns error."""

    httpx_mock.add_response(json=ok_no_fines, status_code=400)

    with pytest.raises(KatError) as ctx:
        await KatApiClient().get_obligations_business(EGN, GOV_ID, BULSTAT)

    assert len(httpx_mock.get_requests()) == 1
    assert isinstance(ctx.value, KatError)
    assert ctx.value.error_type == KatErrorType.API_ERROR
    assert ctx.value.error_subtype == KatErrorSubtype.API_UNKNOWN_ERROR
    assert "unknown error" in ctx.value.error_message


@pytest.mark.asyncio
async def test_check_obligations_api_html_returned(
    httpx_mock: HTTPXMock, err_random_html: pytest.fixture
) -> None:
    """Check obligations - html returned."""

    httpx_mock.add_response(status_code=200, html=err_random_html, headers={
                            'content-type': 'text/html'})

    with pytest.raises(KatError) as ctx:
        await KatApiClient().get_obligations_business(EGN, GOV_ID, BULSTAT)

    assert len(httpx_mock.get_requests()) == 1
    assert isinstance(ctx.value, KatError)
    assert ctx.value.error_type == KatErrorType.API_ERROR
    assert ctx.value.error_subtype == KatErrorSubtype.API_UNKNOWN_ERROR
    assert "malformed response" in ctx.value.error_message


@pytest.mark.asyncio
async def test_check_obligations_api_too_many_requests(
    httpx_mock: HTTPXMock, err_too_many_requests: pytest.fixture
) -> None:
    """Check obligations - too many requests."""

    httpx_mock.add_response(status_code=200, html=err_too_many_requests, headers={
                            'content-type': 'text/html'})

    with pytest.raises(KatError) as ctx:
        await KatApiClient().get_obligations_business(EGN, GOV_ID, BULSTAT)

    assert len(httpx_mock.get_requests()) == 1
    assert isinstance(ctx.value, KatError)
    assert ctx.value.error_type == KatErrorType.API_ERROR
    assert ctx.value.error_subtype == KatErrorSubtype.API_TOO_MANY_REQUESTS
    assert "too many requests" in ctx.value.error_message

# endregion
