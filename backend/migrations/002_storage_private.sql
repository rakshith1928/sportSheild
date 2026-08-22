-- 002: make the 'assets' bucket PRIVATE
--
-- The bucket holds users' sports media (their IP). It was created public,
-- meaning every uploaded file was world-readable by URL — and the 409
-- duplicate response once leaked other users' file_urls.
--
-- The backend now stores only the storage PATH in assets.file_url and
-- hands out short-lived signed URLs (1h) at read time
-- (routers/upload.py: _signed_url / _attach_signed_urls). The service-role
-- key bypasses storage policies, so backend access is unaffected.

update storage.buckets
set public = false
where id = 'assets';
