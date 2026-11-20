# Test Cases

Each case maps to a requirement in the [test plan](TEST_PLAN.md) and to the automated test that checks it.

| ID | Req | Scenario | Expected result | Automated test |
|----|-----|----------|-----------------|----------------|
| TC01 | R1, R2 | Create with only company and position | 201; status `Wishlist`, empty location/notes | `test_rules.py::test_minimal_record_gets_defaults`, `test_create.py::test_create_returns_201_with_id` |
| TC02 | R1 | Surrounding spaces in text fields | Saved trimmed | `test_rules.py::test_whitespace_is_trimmed` |
| TC03 | R1 | Company missing / blank / a number | 400, `company` named | `test_create.py::test_invalid_input_returns_400_naming_the_field` |
| TC04 | R1 | Company of exactly 100 vs 101 characters | 100 accepted, 101 rejected | `test_rules.py::test_boundary_lengths` |
| TC05 | R2 | Status not in the list (`Ghosted`) | 400, `status` named | `test_create.py::test_invalid_input_returns_400_naming_the_field` |
| TC06 | R3 | Applied date today, yesterday, 29 Feb 2024 | Accepted | `test_rules.py::test_dates_up_to_today_are_accepted` |
| TC07 | R3 | Applied date tomorrow | 400 "cannot be in the future" | `test_rules.py::test_date_one_day_in_the_future_is_rejected` |
| TC08 | R3 | 30 Feb, `DD-MM-YYYY`, `YYYYMMDD`, words, a number | 400, `applied_date` named | `test_rules.py::test_malformed_dates_are_rejected` |
| TC09 | R3 | Status `Applied` with no date | 400, `applied_date` named | `test_create.py::test_invalid_input_returns_400_naming_the_field` |
| TC10 | R4 | Every allowed status change (10) | Accepted | `test_rules.py::test_every_allowed_transition_passes` |
| TC11 | R4 | Every forbidden status change (21) | Rejected | `test_rules.py::test_every_forbidden_transition_fails` |
| TC12 | R4 | Applied → Interview → Offer → Accepted via API | Each step 200 | `test_read_update_delete.py::test_patch_follows_status_flow` |
| TC13 | R4 | Rejected → Interview via API | 400 "cannot change from Rejected to Interview" | `test_read_update_delete.py::test_patch_rejects_going_back_from_final_status` |
| TC14 | R5 | Invalid create | Nothing saved | `test_create.py::test_invalid_input_is_not_saved` |
| TC15 | R5 | Invalid update | Record unchanged | `test_read_update_delete.py::test_failed_patch_leaves_record_unchanged` |
| TC16 | R5 | Body is not JSON / a list / null; unknown field; empty patch | 400 | `test_create.py::test_non_object_body_returns_400`, `test_empty_patch_is_400` |
| TC17 | R5 | HTML and SQL-like text in fields | Stored literally; table intact | `test_create.py::test_html_in_notes_is_stored_as_plain_text`, `test_sql_like_input_is_stored_literally` |
| TC18 | R6 | GET/PATCH/DELETE id 999 | 404 `not_found` | `test_read_update_delete.py::test_missing_record_is_404` |
| TC19 | R6 | PUT on the collection | 405 | `test_read_update_delete.py::test_unsupported_method_is_405` |
| TC20 | — | PATCH one field | Only that field changes | `test_read_update_delete.py::test_patch_updates_only_given_fields` |
| TC21 | — | Delete, then get; create again | 404; new id not reused | `test_delete_then_get_is_404`, `test_ids_are_not_reused_after_delete` |
| TC22 | — | Filter list by status; unknown filter | Only matching rows; 400 | `test_list_filters_by_status`, `test_list_with_unknown_status_filter_is_400` |
| TC23 | R7 | Stats on empty data | All zero, rate 0.0 | `test_stats.py::test_stats_when_empty` |
| TC24 | R7 | 1 Wishlist, 2 Applied, 1 Interview | total 4, rate 33.3% | `test_stats.py::test_interview_rate_ignores_wishlist` |
| TC25 | R8 | Open the page with no data | "0 application(s) · interview rate 0.0%", no rows | `e2e/test_ui.py::test_empty_state` |
| TC26 | R8 | Fill the form and submit | Row appears, form clears, count updates | `e2e/test_ui.py::test_add_application_shows_in_table_and_clears_form` |
| TC27 | R8 | Submit without company | Error shown, no row added | `e2e/test_ui.py::test_missing_required_field_shows_error_and_adds_nothing` |
| TC28 | R8 | Submit a future date | Error shown | `e2e/test_ui.py::test_future_date_is_rejected_in_ui` |
| TC29 | R8 | Press Delete on a row | Row removed | `e2e/test_ui.py::test_delete_removes_row` |
| TC30 | R2a | Create with status Interview, Offer, Accepted or Rejected | 400 "must start as Wishlist or Applied"; nothing saved | `test_rules.py::test_new_application_cannot_skip_the_flow`, `api/test_business_rules.py::test_create_with_later_status_is_400` |
| TC31 | R2a, R7 | Create one Applied and one Accepted (BUG-002 steps) | Second is rejected; interview rate stays 0.0% | `api/test_business_rules.py::test_create_as_accepted_no_longer_inflates_interview_rate` |
| TC32 | R2a, R8 | Open the form's status list | Only Wishlist and Applied | `e2e/test_ui.py::test_new_form_offers_only_starting_statuses` |
| TC33 | R4, R8 | Change Applied → Interview from the table | Dropdown lists only allowed steps; status and rate update | `e2e/test_ui.py::test_change_status_from_the_table` |
| TC34 | R4, R8 | Set a row to Rejected | Shown as text, no dropdown | `e2e/test_ui.py::test_final_status_has_no_dropdown` |
| TC35 | R3, R8 | Move a Wishlist row with no date to Applied | Today's date is filled in | `e2e/test_ui.py::test_wishlist_to_applied_fills_todays_date` |
| TC36 | R9 | Add the same company + position again (different case/spacing) | 409; one record kept | `api/test_business_rules.py::test_duplicate_open_application_is_409`, `e2e/test_ui.py::test_duplicate_shows_error` |
| TC37 | R9 | Same company, different position | 201 | `api/test_business_rules.py::test_same_company_different_position_is_allowed` |
| TC38 | R9 | Same role after the old one is Rejected or Accepted | 201 | `api/test_business_rules.py::test_can_apply_again_after_a_closed_application` |
| TC39 | R9 | Same-role matching ignores case and extra spaces | Matches as expected | `test_rules.py::test_same_role_ignores_case_and_spacing` |
