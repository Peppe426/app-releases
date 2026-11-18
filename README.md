# Desktop app releases

Download Windows installers from [Releases](https://github.com/Peppe426/app-releases/releases). Each application has its own release tags and update feed.

| Application | Windows x64 installer releases | Update feed |
| --- | --- | --- |
| JourneyDeck Studio and Runner | [JourneyDeck releases](https://github.com/Peppe426/app-releases/releases?q=journeydeck-v) | [Windows x64](products/journeydeck/windows-x64.json) |

### Publish a program

1. Choose a short, lowercase product name such as `journeydeck`. Create a **draft release in this repository**, with a tag such as `journeydeck-v1.3.0` pointing to `main`. Use a fresh tag for each version.
2. Attach one Windows x64 installer named `<product>-Setup-win-x64.exe`. Capitalization in the filename can match the product branding, for example `JourneyDeck-Setup-win-x64.exe`. Include installation instructions and the changes in the release notes.
3. Publish the release. The **Update product feed** workflow checks the uploaded asset and advances `products/<product>/windows-x64.json` with its version, byte length, and SHA-256. An older release or a prerelease leaves the current stable version in place.
4. For a new application, add a row to the table above. Its updater can read its own feed and download its installer from the matching product tag. Public users can download directly without a GitHub account.

Keep application code, build inputs, and signing credentials in the application's source repository. Upload only the redistributable installer to its release here. To retry a feed update, run **Update product feed** from the Actions tab and enter the published tag.
