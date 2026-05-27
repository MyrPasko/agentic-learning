# PR Review Input

## Title

Add backend endpoint for portfolio summary retrieval

## Summary

This PR adds a new `/api/portfolio` GET endpoint that returns a portfolio summary for the current user.
It introduces request validation for query parameters, a service-layer method for fetching the data,
and updates the API response contract for success and validation-error cases.

## Changed Files

- src/routes/portfolio.ts
- src/services/portfolioService.ts
- src/validators/portfolioValidator.ts
- tests/portfolio.test.ts

## Notes

- The endpoint is read-only.
- The main concerns are API contract clarity, validation behavior, and test coverage.
- No database migration is included in this change.
