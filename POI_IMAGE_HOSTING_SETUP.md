# POI Image Hosting Setup (GitHub + jsDelivr)

## 1) Required path format

All POI images must be stored as:

`assets/poi/<STATE_CODE>/<POI_ID>/<INDEX>.jpg`

Examples:

- `assets/poi/CA/CA_21_solvang/1.jpg`
- `assets/poi/AZ/AZ_01_grand_canyon_south_rim/1.jpg`

Index naming is unpadded and capped at 6 files:

- `1.jpg` ... `6.jpg`

## 2) jsDelivr URL templates

Tag-based (stable, preferred):

`https://cdn.jsdelivr.net/gh/<USER>/<REPO>@<TAG>/assets/poi/<STATE_CODE>/<POI_ID>/<INDEX>.jpg`

For this repo:

`https://cdn.jsdelivr.net/gh/w2olves/epictripwithadam@v1/assets/poi/CA/CA_21_solvang/1.jpg`

Temporary (branch-based):

`https://cdn.jsdelivr.net/gh/w2olves/epictripwithadam@main/assets/poi/CA/CA_21_solvang/1.jpg`

## 3) Git workflow

```bash
git add assets/poi
git commit -m "Add POI images"
git push

git tag v1
git push origin v1
```

When images are updated later:

```bash
git tag v2
git push origin v2
```

## 4) JS URL helper

Use `poi-cdn.js` or this direct helper:

```js
function poiImgUrl({ tag = "v1", stateCode, poiId, index }) {
  return `https://cdn.jsdelivr.net/gh/w2olves/epictripwithadam@${tag}/assets/poi/${stateCode}/${poiId}/${index}.jpg`;
}
```

Example:

```js
poiImgUrl({
  tag: "v1",
  stateCode: "CA",
  poiId: "CA_21_solvang",
  index: 1
});
```

## 5) UI behavior for missing images

Use `poiCdn.renderPoiGallery(...)` from `poi-cdn.js`.

It probes requested image indexes and hides any `<img>` that returns 404 so gallery layout keeps working.

See `codepen-poi-gallery-example.html` for a complete drop-in example.
