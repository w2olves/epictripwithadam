(function (global) {
  "use strict";

  var DEFAULT_USER = "w2olves";
  var DEFAULT_REPO = "epictripwithadam";
  var DEFAULT_TAG = "v1";
  var DEFAULT_MAX_IMAGES = 6;

  function requireField(value, name) {
    if (value === undefined || value === null || value === "") {
      throw new Error("Missing required field: " + name);
    }
  }

  function poiImgUrl(options) {
    options = options || {};
    var user = options.user || DEFAULT_USER;
    var repo = options.repo || DEFAULT_REPO;
    var tag = options.tag || DEFAULT_TAG;
    var stateCode = options.stateCode;
    var poiId = options.poiId;
    var index = options.index;

    requireField(stateCode, "stateCode");
    requireField(poiId, "poiId");
    requireField(index, "index");

    return (
      "https://cdn.jsdelivr.net/gh/" +
      user +
      "/" +
      repo +
      "@" +
      tag +
      "/assets/poi/" +
      stateCode +
      "/" +
      poiId +
      "/" +
      index +
      ".jpg"
    );
  }

  function resolveImageIndices(poi, maxImages) {
    maxImages = maxImages || DEFAULT_MAX_IMAGES;

    if (Array.isArray(poi.images) && poi.images.length > 0) {
      return poi.images;
    }

    if (Number.isInteger(poi.imagesCount) && poi.imagesCount > 0) {
      var capped = Math.min(poi.imagesCount, maxImages);
      return Array.from({ length: capped }, function (_, i) {
        return i + 1;
      });
    }

    return Array.from({ length: maxImages }, function (_, i) {
      return i + 1;
    });
  }

  function poiImageUrls(poi, options) {
    options = options || {};
    var indices = resolveImageIndices(poi, options.maxImages);
    return indices.map(function (index) {
      return poiImgUrl({
        user: options.user,
        repo: options.repo,
        tag: options.tag || DEFAULT_TAG,
        stateCode: poi.stateCode,
        poiId: poi.poiId,
        index: index,
      });
    });
  }

  function hideBrokenImage(img) {
    var slot = img.closest("[data-poi-image-slot]");
    if (slot) {
      slot.style.display = "none";
      return;
    }
    img.style.display = "none";
  }

  function renderPoiGallery(container, poi, options) {
    options = options || {};
    var urls = poiImageUrls(poi, options);

    container.innerHTML = "";
    urls.forEach(function (url, idx) {
      var slot = document.createElement("div");
      slot.className = options.slotClassName || "poi-image-slot";
      slot.setAttribute("data-poi-image-slot", "");

      var img = document.createElement("img");
      img.className = options.imageClassName || "poi-image";
      img.alt = (poi.displayName || poi.poiId) + " image " + (idx + 1);
      img.loading = "lazy";
      img.src = url;
      img.onerror = function () {
        hideBrokenImage(img);
      };

      slot.appendChild(img);
      container.appendChild(slot);
    });
  }

  global.poiCdn = {
    poiImgUrl: poiImgUrl,
    poiImageUrls: poiImageUrls,
    renderPoiGallery: renderPoiGallery,
    hideBrokenImage: hideBrokenImage,
  };
})(typeof window !== "undefined" ? window : globalThis);
