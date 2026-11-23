# App releases

Download signed Windows installers and Android APKs from [Releases](https://github.com/Peppe426/app-releases/releases). Each application has its own release tags and platform feeds.

| Application | Installer releases | Update feeds |
| --- | --- | --- |
| Hemloop | [Hemloop releases](https://github.com/Peppe426/app-releases/releases?q=hemloop-v) | `products/hemloop/android.json` after the first release |
| JourneyDeck Studio and Runner | [JourneyDeck releases](https://github.com/Peppe426/app-releases/releases?q=journeydeck-v) | [Windows x64](products/journeydeck/windows-x64.json) |
| MeetingHand | [MeetingHand releases](https://github.com/Peppe426/app-releases/releases?q=meetinghand-v) | [Windows x64](products/meetinghand/windows-x64.json) · [Android](products/meetinghand/android.json) |

### Personal MSIX signing certificate

Peter Liljeholm signs personal Windows packages with the [Peter Liljeholm public code-signing certificate](certificates/Peter-Liljeholm-Code-Signing.cer). Its issuer and subject are `CN=Peter Liljeholm`. The certificate expires on 9 October 2031.

On a new PC, download the public certificate and verify its SHA-256 fingerprint before trusting it. In PowerShell, run:

```powershell
Get-FileHash .\Peter-Liljeholm-Code-Signing.cer -Algorithm SHA256
```

The expected fingerprint is `FF01858EBEF37FF3EA49D04FDF273E6AA0350208B5C46A22FC2BB82C9EF56B60`. To trust this publisher on your PC, import the verified certificate in an **administrator** PowerShell:

```powershell
Import-Certificate -FilePath .\Peter-Liljeholm-Code-Signing.cer -CertStoreLocation Cert:\LocalMachine\TrustedPeople
```

For another personal project, use `Publisher="CN=Peter Liljeholm"` in its MSIX manifest and sign with certificate thumbprint `C8A97D64E171DCDF5256D9E55800380B8AF5B51A` from the signing machine's Current User personal store. The private key stays in that store.

### Publish a program

1. Choose a short, lowercase product name such as `journeydeck`. Create a **draft release in this repository**, with a tag such as `journeydeck-v1.3.0` pointing to `main`. Use a fresh tag for each version.
2. Attach the installer for each platform being released. Use `<product>-Setup-win-x64.exe` or `<product>-Setup-win-x64.msix` for Windows, `MeetingHand-Android.apk` for MeetingHand, and `Hemloop-Android.apk` for Hemloop. Hemloop's APK supports ARM64 and x64. Keep the exact filename and signing identity for future versions. Include installation instructions and the changes in the release notes.
3. Publish the release. The **Update product feed** workflow records the version, byte length, and SHA-256 for each attached installer in its platform feed. A Hemloop Android release advances `products/hemloop/android.json`. Older releases and prereleases leave the current stable versions in place.
4. For a new application, add a row to the table above. Its updater can read its own feed and download its installer from the matching product tag. Public users can download directly without a GitHub account.

Keep application code and build inputs in the application's source repository. Keep private signing keys in the signing machine's certificate store. Upload the redistributable installer to its release here. To retry a feed update, run **Update product feed** from the Actions tab and enter the published tag.
