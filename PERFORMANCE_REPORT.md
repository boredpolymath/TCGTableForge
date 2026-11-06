# Performance check

Measured 2026-11-05 on a MacBook Air (Mac14,15), Apple M2, 8 GB RAM, macOS 27.2, using Google Chrome 156.0.8078.81 in headless mode.

The repeatable fixture contains 500 cards and 1,000 relationships. Three runs produced these median timings:

| Operation | Median | SRS target |
|---|---:|---:|
| Project open to `DOMContentLoaded` | 60.1 ms | Under 2,000 ms |
| Type filtering | 6.6 ms | Under 2,000 ms |
| Search | 3.4 ms | Informational |
| Board/List switch | 2.5 ms | Informational |
| Card edit and re-render | 38.5 ms | Informational |

The measured JavaScript heap after the fixture opened was about 7.1 MB. All measured operations were below the two-second opening and filtering target. Run `npm run fixture` to regenerate the input and `npm run test:performance` to repeat the measurement.

A later Chrome run on the same device reported 90.1 ms open, 7.8 ms filter, 5.0 ms search, 3.0 ms Board/List switch, and 40.0 ms edit, with a 7.1 MB heap. It also met the SRS target.

A stress run used one card with a 3,000-character note and switched among three projects ten times. Project open was 82.4 ms, filtering 5.5 ms, search 3.6 ms, Board/List switching 2.3 ms, ten project switches 98.7 ms, and edit/re-render 40.1 ms. The measured JavaScript heap was 9.8 MB. The SRS open and filtering targets remained satisfied.
