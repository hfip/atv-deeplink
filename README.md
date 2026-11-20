# atv-deeplink

Deep links for Apple TV are hand-written strings with a percent-encoded URL inside another
URL, and the only way to find out you got it wrong is to type it into a device.

```bash
$ atv-deeplink build infuse "smb://nas/media/فيلم جديد.mkv"
infuse://x-callback-url/play?url=smb%3A%2F%2Fnas%2Fmedia%2F%D9%81%D9%8A%D9%84%D9%85%20%D8%AC%D8%AF%D9%8A%D8%AF.mkv

$ atv-deeplink check "infuse://x-callback-url/play?url=a b"
error infuse://x-callback-url/play?url=a b
      error   raw space in the URL; encode it as %20
```

## Known apps

| key | app | link shape |
| --- | --- | --- |
| `infuse` | Infuse | `infuse://x-callback-url/play?url=…` |
| `vlc` | VLC | `vlc-x-callback://x-callback-url/stream?url=…` |
| `youtube` | YouTube | `youtube://watch?v=…` |

That is the whole list on purpose. tvOS URL schemes are undocumented and each app does its
own thing; guessing a scheme for Netflix or Plex would just produce links that silently do
nothing. Adding an app is a five-line change in `apps.py`.

## Install

```bash
pipx install git+https://github.com/hfip/atv-deeplink.git
```

## Use

```bash
atv-deeplink build infuse "smb://nas/movies/Dune.mkv"
atv-deeplink check "infuse://x-callback-url/play?url=..."
atv-deeplink apps
atv-deeplink --json check "$URL"
```

`check` distinguishes errors from warnings: a web URL or a missing required parameter is an
error, an unknown scheme is only a warning because the app may exist outside this list.

Exit codes: `0` ok, `1` at least one link has an error, `2` bad usage.

## Testing on a simulator

Deep links can be opened on a tvOS simulator directly:

```bash
xcrun simctl openurl booted "$(atv-deeplink build infuse 'smb://nas/movie.mkv')"
```

On a physical Apple TV there is no equivalent command; you are back to typing the URL in
Safari or your own test harness.

## What it does not do

- It does not verify that the receiving app accepts the payload, only that the link is
  well-formed.
- It does not know undocumented schemes, and it will not invent one.
- It does not talk to the device. `simctl` does that, not this tool.

## بالعربي

<div dir="rtl" align="right">

روابط tvOS العميقة عبارة عن رابط داخل رابط مع ترميز percent، وأي خطأ ما يبان إلا على
الجهاز. الأداة تبني الرابط وترمزه صح:

```bash
atv-deeplink build infuse "smb://nas/فيلم جديد.mkv"
atv-deeplink check "$URL"
```

الأسماء المعروفة ثلاثة فقط (Infuse، VLC، YouTube) لأن بقية التطبيقات ما توثّق مخططها،
والتخمين ينتج روابط صامتة ما تسوي شي.

</div>

## License

MIT. See [LICENSE](LICENSE).
