# API route inventory

Generated from the local router registrations and endpoint signatures. Dependencies listed here are not proof of complete authorization; checks inside each handler also matter. Device routes have two registered prefixes.

| Method | Path | Declared dependencies | Source |
|---|---|---|---|
| GET | `/api/v1/academic/classes` | `get_db, get_current_admin` | [backend/app/api/academic.py:90](../backend/app/api/academic.py#L90) |
| POST | `/api/v1/academic/classes` | `get_db, get_current_admin` | [backend/app/api/academic.py:59](../backend/app/api/academic.py#L59) |
| PUT | `/api/v1/academic/classes/{class_id}` | `get_db, get_current_admin` | [backend/app/api/academic.py:71](../backend/app/api/academic.py#L71) |
| GET | `/api/v1/academic/departments` | `get_db, get_current_admin` | [backend/app/api/academic.py:27](../backend/app/api/academic.py#L27) |
| POST | `/api/v1/academic/departments` | `get_db, get_current_admin` | [backend/app/api/academic.py:34](../backend/app/api/academic.py#L34) |
| DELETE | `/api/v1/academic/departments/{department_id}` | `get_db, get_current_admin` | [backend/app/api/academic.py:46](../backend/app/api/academic.py#L46) |
| GET | `/api/v1/academic/faculty/live-class` | `get_db, get_current_management_or_faculty` | [backend/app/api/academic.py:445](../backend/app/api/academic.py#L445) |
| POST | `/api/v1/academic/faculty/marks` | `get_db, get_current_management_or_faculty` | [backend/app/api/academic.py:374](../backend/app/api/academic.py#L374) |
| POST | `/api/v1/academic/faculty/students/{student_id}/remarks` | `get_db, get_current_management_or_faculty` | [backend/app/api/academic.py:426](../backend/app/api/academic.py#L426) |
| GET | `/api/v1/academic/faculty/weekly-schedule` | `get_db, get_current_management_or_faculty` | [backend/app/api/academic.py:511](../backend/app/api/academic.py#L511) |
| GET | `/api/v1/academic/sections` | `get_db, get_current_management_or_faculty` | [backend/app/api/academic.py:171](../backend/app/api/academic.py#L171) |
| POST | `/api/v1/academic/sections` | `get_db, get_current_admin` | [backend/app/api/academic.py:98](../backend/app/api/academic.py#L98) |
| POST | `/api/v1/academic/sections/{section_id}/assign` | `get_db, get_current_admin` | [backend/app/api/academic.py:115](../backend/app/api/academic.py#L115) |
| DELETE | `/api/v1/academic/sections/{section_id}/assign/{faculty_user_id}` | `get_db, get_current_admin` | [backend/app/api/academic.py:143](../backend/app/api/academic.py#L143) |
| GET | `/api/v1/academic/students` | `get_db, get_current_management_or_faculty` | [backend/app/api/academic.py:323](../backend/app/api/academic.py#L323) |
| POST | `/api/v1/academic/students/bulk` | `get_db, get_current_admin` | [backend/app/api/academic.py:197](../backend/app/api/academic.py#L197) |
| DELETE | `/api/v1/academic/students/{student_id}` | `get_db, get_current_admin` | [backend/app/api/academic.py:305](../backend/app/api/academic.py#L305) |
| PUT | `/api/v1/academic/students/{student_id}` | `get_db, get_current_admin` | [backend/app/api/academic.py:234](../backend/app/api/academic.py#L234) |
| GET | `/api/v1/academic/timetable/faculty/list` | `get_db, get_current_admin` | [backend/app/api/timetable.py:83](../backend/app/api/timetable.py#L83) |
| POST | `/api/v1/academic/timetable/save` | `get_db, get_current_admin` | [backend/app/api/timetable.py:108](../backend/app/api/timetable.py#L108) |
| DELETE | `/api/v1/academic/timetable/{section_id}` | `get_db, get_current_admin` | [backend/app/api/timetable.py:243](../backend/app/api/timetable.py#L243) |
| GET | `/api/v1/academic/timetable/{section_id}` | `get_db, get_current_management_or_faculty` | [backend/app/api/timetable.py:39](../backend/app/api/timetable.py#L39) |
| GET | `/api/v1/admin/` | `None declared` | [backend/app/api/consumers/admin.py:22](../backend/app/api/consumers/admin.py#L22) |
| POST | `/api/v1/admin/{tenant_id}/smart-build` | `get_db` | [backend/app/api/consumers/admin.py:26](../backend/app/api/consumers/admin.py#L26) |
| GET | `/api/v1/analytics/` | `None declared` | [backend/app/api/consumers/analytics.py:22](../backend/app/api/consumers/analytics.py#L22) |
| GET | `/api/v1/analytics/{tenant_id}/attendance-prediction` | `None declared` | [backend/app/api/consumers/analytics.py:7](../backend/app/api/consumers/analytics.py#L7) |
| GET | `/api/v1/analytics/{tenant_id}/faculty-insights` | `None declared` | [backend/app/api/consumers/analytics.py:15](../backend/app/api/consumers/analytics.py#L15) |
| GET | `/api/v1/attendance/report` | `get_db, get_current_management_or_faculty` | [backend/app/api/attendance.py:500](../backend/app/api/attendance.py#L500) |
| GET | `/api/v1/attendance/reports/weekly` | `get_db, get_current_management_or_faculty` | [backend/app/api/attendance.py:514](../backend/app/api/attendance.py#L514) |
| GET | `/api/v1/attendance/stats/overview` | `get_db, get_current_management_or_faculty` | [backend/app/api/attendance.py:54](../backend/app/api/attendance.py#L54) |
| GET | `/api/v1/attendance/status` | `get_db, get_current_faculty` | [backend/app/api/attendance.py:19](../backend/app/api/attendance.py#L19) |
| POST | `/api/v1/attendance/submit` | `get_db, get_current_faculty` | [backend/app/api/attendance.py:225](../backend/app/api/attendance.py#L225) |
| POST | `/api/v1/attendance/submit/smart` | `get_db, get_current_faculty` | [backend/app/api/attendance.py:361](../backend/app/api/attendance.py#L361) |
| POST | `/api/v1/auth/google` | `get_db` | [backend/app/api/auth.py:52](../backend/app/api/auth.py#L52) |
| POST | `/api/v1/auth/login` | `get_db` | [backend/app/api/auth.py:16](../backend/app/api/auth.py#L16) |
| POST | `/api/v1/auth/passwordless` | `get_db` | [backend/app/api/auth.py:101](../backend/app/api/auth.py#L101) |
| GET | `/api/v1/device/` | `get_db, get_current_management_or_faculty` | [backend/app/api/device.py:63](../backend/app/api/device.py#L63) |
| POST | `/api/v1/device/generate-token` | `get_db, get_current_management_or_faculty` | [backend/app/api/device.py:69](../backend/app/api/device.py#L69) |
| POST | `/api/v1/device/heartbeat` | `get_db` | [backend/app/api/device.py:166](../backend/app/api/device.py#L166) |
| POST | `/api/v1/device/register` | `get_db` | [backend/app/api/device.py:113](../backend/app/api/device.py#L113) |
| DELETE | `/api/v1/device/{device_id}` | `get_db, get_current_management_or_faculty` | [backend/app/api/device.py:85](../backend/app/api/device.py#L85) |
| PATCH | `/api/v1/device/{device_id}` | `get_db, get_current_management_or_faculty` | [backend/app/api/device.py:99](../backend/app/api/device.py#L99) |
| GET | `/api/v1/devices/` | `get_db, get_current_management_or_faculty` | [backend/app/api/device.py:63](../backend/app/api/device.py#L63) |
| POST | `/api/v1/devices/generate-token` | `get_db, get_current_management_or_faculty` | [backend/app/api/device.py:69](../backend/app/api/device.py#L69) |
| POST | `/api/v1/devices/heartbeat` | `get_db` | [backend/app/api/device.py:166](../backend/app/api/device.py#L166) |
| POST | `/api/v1/devices/register` | `get_db` | [backend/app/api/device.py:113](../backend/app/api/device.py#L113) |
| DELETE | `/api/v1/devices/{device_id}` | `get_db, get_current_management_or_faculty` | [backend/app/api/device.py:85](../backend/app/api/device.py#L85) |
| PATCH | `/api/v1/devices/{device_id}` | `get_db, get_current_management_or_faculty` | [backend/app/api/device.py:99](../backend/app/api/device.py#L99) |
| GET | `/api/v1/faculty/` | `None declared` | [backend/app/api/consumers/faculty.py:28](../backend/app/api/consumers/faculty.py#L28) |
| GET | `/api/v1/faculty/{tenant_id}/derive-session` | `None declared` | [backend/app/api/consumers/faculty.py:7](../backend/app/api/consumers/faculty.py#L7) |
| GET | `/api/v1/institutions/` | `get_db, get_current_superadmin` | [backend/app/api/institution.py:111](../backend/app/api/institution.py#L111) |
| POST | `/api/v1/institutions/` | `get_db, get_current_superadmin` | [backend/app/api/institution.py:95](../backend/app/api/institution.py#L95) |
| GET | `/api/v1/institutions/me/settings` | `get_db, get_current_active_user` | [backend/app/api/institution.py:139](../backend/app/api/institution.py#L139) |
| PATCH | `/api/v1/institutions/me/settings` | `get_db, get_current_active_user` | [backend/app/api/institution.py:163](../backend/app/api/institution.py#L163) |
| POST | `/api/v1/institutions/provision` | `get_db, get_current_superadmin` | [backend/app/api/institution.py:15](../backend/app/api/institution.py#L15) |
| GET | `/api/v1/institutions/reports/detailed` | `get_db, get_current_superadmin` | [backend/app/api/institution.py:205](../backend/app/api/institution.py#L205) |
| GET | `/api/v1/institutions/with-admins` | `get_db, get_current_superadmin` | [backend/app/api/institution.py:77](../backend/app/api/institution.py#L77) |
| DELETE | `/api/v1/institutions/{institution_id}` | `get_db, get_current_superadmin` | [backend/app/api/institution.py:277](../backend/app/api/institution.py#L277) |
| GET | `/api/v1/institutions/{institution_id}` | `get_db, get_current_active_user` | [backend/app/api/institution.py:121](../backend/app/api/institution.py#L121) |
| GET | `/api/v1/legacy-notifications/logs` | `get_db, get_current_management_or_faculty` | [backend/app/api/notification.py:28](../backend/app/api/notification.py#L28) |
| POST | `/api/v1/legacy-sms/ack` | `get_db` | [backend/app/api/sms.py:122](../backend/app/api/sms.py#L122) |
| GET | `/api/v1/legacy-sms/pending` | `get_db` | [backend/app/api/sms.py:41](../backend/app/api/sms.py#L41) |
| GET | `/api/v1/legacy-sms/queue` | `get_db` | [backend/app/api/sms.py:41](../backend/app/api/sms.py#L41) |
| GET | `/api/v1/legacy-sms/stats` | `get_db, get_current_management_or_faculty` | [backend/app/api/sms.py:195](../backend/app/api/sms.py#L195) |
| POST | `/api/v1/legacy-sms/status` | `get_db` | [backend/app/api/sms.py:140](../backend/app/api/sms.py#L140) |
| POST | `/api/v1/legacy-sms/update-status` | `get_db` | [backend/app/api/sms.py:140](../backend/app/api/sms.py#L140) |
| GET | `/api/v1/management/` | `None declared` | [backend/app/api/consumers/management.py:39](../backend/app/api/consumers/management.py#L39) |
| POST | `/api/v1/management/academic/smart-promote-semester` | `get_db, get_current_management` | [backend/app/api/consumers/management.py:179](../backend/app/api/consumers/management.py#L179) |
| GET | `/api/v1/management/analytics/enterprise` | `get_db, get_current_management` | [backend/app/api/consumers/management.py:198](../backend/app/api/consumers/management.py#L198) |
| GET | `/api/v1/management/events` | `get_db, get_current_management` | [backend/app/api/consumers/management.py:60](../backend/app/api/consumers/management.py#L60) |
| POST | `/api/v1/management/events` | `get_db, get_current_management` | [backend/app/api/consumers/management.py:43](../backend/app/api/consumers/management.py#L43) |
| GET | `/api/v1/management/leaves` | `get_db, get_current_management` | [backend/app/api/consumers/management.py:102](../backend/app/api/consumers/management.py#L102) |
| PUT | `/api/v1/management/leaves/{id}/status` | `get_db, get_current_management` | [backend/app/api/consumers/management.py:130](../backend/app/api/consumers/management.py#L130) |
| GET | `/api/v1/management/reports/master-attendance-sheet` | `get_db, get_current_management` | [backend/app/api/consumers/management.py:166](../backend/app/api/consumers/management.py#L166) |
| GET | `/api/v1/management/student/{student_id}/dashboard` | `get_db, get_current_active_user` | [backend/app/api/consumers/management.py:70](../backend/app/api/consumers/management.py#L70) |
| POST | `/api/v1/management/student/{student_id}/documents` | `get_db, get_current_management` | [backend/app/api/consumers/management.py:146](../backend/app/api/consumers/management.py#L146) |
| GET | `/api/v1/notifications/` | `None declared` | [backend/app/api/consumers/notifications_engine.py:35](../backend/app/api/consumers/notifications_engine.py#L35) |
| POST | `/api/v1/notifications/dispatch` | `None declared` | [backend/app/api/consumers/notifications_engine.py:27](../backend/app/api/consumers/notifications_engine.py#L27) |
| POST | `/api/v1/parent/auth/link-student` | `get_db` | [backend/app/api/consumers/parent.py:75](../backend/app/api/consumers/parent.py#L75) |
| POST | `/api/v1/parent/auth/request-otp` | `get_db` | [backend/app/api/consumers/parent.py:31](../backend/app/api/consumers/parent.py#L31) |
| POST | `/api/v1/parent/auth/verify-otp` | `get_db` | [backend/app/api/consumers/parent.py:41](../backend/app/api/consumers/parent.py#L41) |
| GET | `/api/v1/parent/dashboard` | `get_db, get_current_user` | [backend/app/api/consumers/parent.py:91](../backend/app/api/consumers/parent.py#L91) |
| GET | `/api/v1/parent/documents` | `get_db, get_current_user` | [backend/app/api/consumers/parent.py:240](../backend/app/api/consumers/parent.py#L240) |
| GET | `/api/v1/parent/faculty` | `get_db, get_current_user` | [backend/app/api/consumers/parent.py:253](../backend/app/api/consumers/parent.py#L253) |
| GET | `/api/v1/parent/fees/balance` | `get_current_user` | [backend/app/api/consumers/parent.py:284](../backend/app/api/consumers/parent.py#L284) |
| GET | `/api/v1/parent/leaves` | `get_db, get_current_user` | [backend/app/api/consumers/parent.py:227](../backend/app/api/consumers/parent.py#L227) |
| POST | `/api/v1/parent/leaves` | `get_db, get_current_user` | [backend/app/api/consumers/parent.py:208](../backend/app/api/consumers/parent.py#L208) |
| GET | `/api/v1/parent/profile` | `get_db, get_current_user` | [backend/app/api/consumers/parent.py:150](../backend/app/api/consumers/parent.py#L150) |
| GET | `/api/v1/reports/` | `None declared` | [backend/app/api/consumers/reports.py:26](../backend/app/api/consumers/reports.py#L26) |
| GET | `/api/v1/reports/{tenant_id}/generate` | `None declared` | [backend/app/api/consumers/reports.py:8](../backend/app/api/consumers/reports.py#L8) |
| GET | `/api/v1/sms/` | `None declared` | [backend/app/api/consumers/sms_gateway.py:6](../backend/app/api/consumers/sms_gateway.py#L6) |
| GET | `/api/v1/student/` | `None declared` | [backend/app/api/consumers/student.py:6](../backend/app/api/consumers/student.py#L6) |
| GET | `/api/v1/users/` | `get_db, get_current_management` | [backend/app/api/user.py:110](../backend/app/api/user.py#L110) |
| GET | `/api/v1/users/faculty` | `get_db, get_current_management` | [backend/app/api/user.py:117](../backend/app/api/user.py#L117) |
| POST | `/api/v1/users/faculty` | `get_db, get_current_management` | [backend/app/api/user.py:15](../backend/app/api/user.py#L15) |
| DELETE | `/api/v1/users/faculty/{user_id}` | `get_db, get_current_management` | [backend/app/api/user.py:136](../backend/app/api/user.py#L136) |
| PUT | `/api/v1/users/faculty/{user_id}` | `get_db, get_current_management` | [backend/app/api/user.py:154](../backend/app/api/user.py#L154) |
| POST | `/api/v1/users/student` | `get_db, get_current_management_or_faculty` | [backend/app/api/user.py:81](../backend/app/api/user.py#L81) |
