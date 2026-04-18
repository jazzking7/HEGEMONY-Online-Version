class TerritoryView {
  constructor(data, id, textures, callbacks = {}) {
    this.data = data;
    this.id = id;
    this.textures = textures;
    this.onHover = callbacks.onHover || null;
    this.onOut = callbacks.onOut || null;
    this.onClick = callbacks.onClick || null;
    this.viewMode = "near";

    this.container = new PIXI.Container();

    this.base = new PIXI.Graphics();
    this.border = new PIXI.Graphics();
    this.hit = new PIXI.Graphics();
    this.iconLayer = new PIXI.Container();
    this.capitalLayer = new PIXI.Container();
    this.capitalGraphic = new PIXI.Graphics();

    this.nameStyleDark = new PIXI.TextStyle({
      fontFamily: "Urbanist",
      fontSize: 12,
      fill: 0x000000,
      fontWeight: "700",
      align: "left"
    });

    this.nameStyleLight = new PIXI.TextStyle({
      fontFamily: "Urbanist",
      fontSize: 12,
      fill: 0xf5f5f5,
      fontWeight: "700",
      align: "left"
    });

    this.troopNearStyleDark = new PIXI.TextStyle({
      fontFamily: "Urbanist",
      fontSize: 16,
      fill: 0x000000,
      fontWeight: "700",
      align: "left"
    });

    this.troopNearStyleLight = new PIXI.TextStyle({
      fontFamily: "Urbanist",
      fontSize: 16,
      fill: 0xf5f5f5,
      fontWeight: "700",
      align: "left"
    });

    this.troopFarStyleDark = new PIXI.TextStyle({
      fontFamily: "Urbanist",
      fontSize: 35,
      fill: 0x000000,
      fontWeight: "700",
      align: "left"
    });

    this.troopFarStyleLight = new PIXI.TextStyle({
      fontFamily: "Urbanist",
      fontSize: 35,
      fill: 0xf5f5f5,
      fontWeight: "700",
      align: "left"
    });

    this.nameText = new PIXI.Text({
      text: this.data.name || "",
      style: this.nameStyleDark
    });

    this.troopText = new PIXI.Text({
      text: this.data.troops != null ? String(this.data.troops) : "",
      style: this.troopNearStyleDark
    });

    this.nameText.resolution = 2;
    this.troopText.resolution = 2;
    this.nameText.roundPixels = true;
    this.troopText.roundPixels = true;

    this.devSprite = null;
    this.insigSprite = null;
    this.hallSprite = null;
    this.leylineSprite = null;

    this.capitalLayer.addChild(this.capitalGraphic);

    this.container.addChild(this.base);
    this.container.addChild(this.border);
    this.container.addChild(this.iconLayer);
    this.container.addChild(this.capitalLayer);
    this.container.addChild(this.hit);
    this.container.addChild(this.nameText);
    this.container.addChild(this.troopText);

    this.drawPolygon();
    this.refreshTextStyles();
    this.layoutForMode("near");
    this.makeInteractive();
    this.syncIcons();
    this.setCapitalState({});
  }

  getFlatPoints() {
    const pts = [];
    const outline = this.data.outline || [];
    for (let i = 0; i < outline.length; i++) {
      pts.push(outline[i].x, outline[i].y);
    }
    return pts;
  }

  toPixiColor(colorValue) {
    if (typeof colorValue === "number") return colorValue;

    if (typeof colorValue === "string") {
      if (colorValue.startsWith("#")) return parseInt(colorValue.slice(1), 16);

      const named = {
        white: 0xffffff,
        black: 0x000000,
        red: 0xff0000,
        green: 0x00ff00,
        blue: 0x0000ff,
        yellow: 0xffff00,
        gray: 0x808080,
        grey: 0x808080
      };

      const lower = colorValue.toLowerCase();
      if (named[lower] !== undefined) return named[lower];
    }

    return 0xffffff;
  }

  getBrightnessFromColorValue(colorValue) {
    const c = this.toPixiColor(colorValue || "#ffffff");
    const r = (c >> 16) & 255;
    const g = (c >> 8) & 255;
    const b = c & 255;
    return (0.299 * r) + (0.587 * g) + (0.114 * b);
  }

  isDarkFill() {
    return this.getBrightnessFromColorValue(this.data.color || "#ffffff") < 128;
  }

  drawPolygon() {
    const pts = this.getFlatPoints();
    const fillColor = this.toPixiColor(this.data.color || "#ffffff");

    this.base.clear();
    this.base.poly(pts);
    this.base.fill(fillColor);

    this.border.clear();
    this.border.poly(pts);
    this.border.stroke({
      color: 0x7a95a3,
      width: 3.2,
      join: "round"
    });

    this.hit.clear();
    this.hit.poly(pts);
    this.hit.fill({
      color: 0xffffff,
      alpha: 0.001
    });
  }

  refreshTextStyles() {
    const darkFill = this.isDarkFill();

    if (darkFill) {
      if (this.nameText.style !== this.nameStyleLight) {
        this.nameText.style = this.nameStyleLight;
      }
      if (this.viewMode === "far") {
        if (this.troopText.style !== this.troopFarStyleLight) {
          this.troopText.style = this.troopFarStyleLight;
        }
      } else {
        if (this.troopText.style !== this.troopNearStyleLight) {
          this.troopText.style = this.troopNearStyleLight;
        }
      }
    } else {
      if (this.nameText.style !== this.nameStyleDark) {
        this.nameText.style = this.nameStyleDark;
      }
      if (this.viewMode === "far") {
        if (this.troopText.style !== this.troopFarStyleDark) {
          this.troopText.style = this.troopFarStyleDark;
        }
      } else {
        if (this.troopText.style !== this.troopNearStyleDark) {
          this.troopText.style = this.troopNearStyleDark;
        }
      }
    }
  }

  layoutNear() {
    if (this.data.ns) {
      this.nameText.position.set(
        Math.round(this.data.ns.x),
        Math.round(this.data.ns.y - 12)
      );
    }

    if (this.data.ts) {
      this.troopText.position.set(
        Math.round(this.data.ts.x),
        Math.round(this.data.ts.y - 16)
      );
    }
  }

  layoutFar() {
    if (this.data.cps) {
      this.troopText.position.set(
        Math.round(this.data.cps.x),
        Math.round(this.data.cps.y - 35)
      );
    }
  }

  layoutForMode(mode) {
    this.viewMode = mode;

    if (mode === "far") {
      this.nameText.visible = false;
      this.troopText.visible = true;
      this.iconLayer.visible = false;
      this.capitalLayer.visible = false;
      this.refreshTextStyles();
      this.layoutFar();
      return;
    }

    this.nameText.visible = true;
    this.troopText.visible = true;
    this.iconLayer.visible = true;
    this.capitalLayer.visible = true;
    this.refreshTextStyles();
    this.layoutNear();
  }

  makeInteractive() {
    const pts = this.getFlatPoints();

    this.hit.eventMode = "static";
    this.hit.cursor = "pointer";
    this.hit.hitArea = new PIXI.Polygon(pts);

    this.hit.on("pointerover", () => {
      if (this.onHover) this.onHover(this.id);
    });

    this.hit.on("pointerout", () => {
      if (this.onOut) this.onOut(this.id);
    });

    this.hit.on("pointertap", () => {
      if (this.onClick) this.onClick(this.id);
    });
  }

  ensureSprite(slotName, textureKey) {
    if (!this[slotName]) {
      this[slotName] = new PIXI.Sprite(this.textures[textureKey]);
      this[slotName].visible = false;
      this.iconLayer.addChild(this[slotName]);
    }
    return this[slotName];
  }

  syncIcons() {
    const dev = this.ensureSprite("devSprite", "city");
    const insig = this.ensureSprite("insigSprite", "fort");
    const hall = this.ensureSprite("hallSprite", "hall");
    const leyline = this.ensureSprite("leylineSprite", "leyline");

    dev.visible = false;
    insig.visible = false;
    hall.visible = false;
    leyline.visible = false;

    if (this.data.devImg && this.data.ds) {
      let devKey = "city";
      if (this.data.devImg === "megacity") devKey = "megacity";
      if (this.data.devImg === "nexus") devKey = "nexus";
      if (this.data.devImg === "bureau") devKey = "bureau";

      dev.texture = this.textures[devKey];
      dev.x = this.data.ds.x;
      dev.y = this.data.ds.y;
      dev.width = this.data.ds.dx;
      dev.height = this.data.ds.dy;
      dev.visible = true;
    }

    if (this.data.insig && this.data.is) {
      let insigKey = "fort";
      if (this.data.insig === "bureau") insigKey = "bureau";
      if (this.data.insig === "hall") insigKey = "hall";
      if (this.data.insig === "leyline") insigKey = "leyline";

      insig.texture = this.textures[insigKey];
      insig.x = this.data.is.x;
      insig.y = this.data.is.y;
      insig.width = this.data.is.dx;
      insig.height = this.data.is.dy;
      insig.visible = true;
    }

    if (this.data.hallImg && this.data.cs) {
      hall.texture = this.textures.hall;
      hall.x = this.data.cs.x;
      hall.y = this.data.cs.y;
      hall.width = this.data.cs.dx;
      hall.height = this.data.cs.dy;
      hall.visible = true;
    }

    if (this.data.leylineImg && this.data.cs) {
      const tex = this.textures.leyline;
      const baseW = tex.orig ? tex.orig.width : tex.width;
      const baseH = tex.orig ? tex.orig.height : tex.height;
      const targetH = this.data.cs.dy;
      const scaledW = baseW * (targetH / baseH);

      leyline.texture = tex;
      leyline.x = this.data.cs.x;
      leyline.y = this.data.cs.y;
      leyline.width = scaledW;
      leyline.height = targetH;
      leyline.visible = true;
    }
  }

  createStarPoints(centerX, centerY, outerRadius, innerRadius, numPoints = 5) {
    const pts = [];
    const angleStep = Math.PI / numPoints;
    let angle = -Math.PI / 2;

    for (let i = 0; i < numPoints * 2; i++) {
      const radius = i % 2 === 0 ? outerRadius : innerRadius;
      pts.push(
        centerX + Math.cos(angle) * radius,
        centerY + Math.sin(angle) * radius
      );
      angle += angleStep;
    }

    return pts;
  }

  setCapitalState(capitalState = {}) {
    if ("isCapital" in capitalState) {
      this.data.isCapital = capitalState.isCapital;
    }

    if ("capital_color" in capitalState) {
      this.data.capital_color = capitalState.capital_color;
    }

    if (this.data.capital_color == null) {
      this.data.capital_color = "#ffffff";
    }

    this.capitalGraphic.clear();

    if (!this.data.isCapital || !this.data.cs) return;

    const x = this.data.cs.x;
    const y = this.data.cs.y;
    const w = this.data.cs.dx;
    const h = this.data.cs.dy;

    const centerX = x + w / 2;
    const centerY = y + h / 2;
    const starSize = Math.min(w, h) * 0.8;
    const outerRadius = starSize / 2;
    const innerRadius = starSize / 4;

    const fillColor = this.toPixiColor(this.data.capital_color || "#ffffff");
    const luminance = this.getBrightnessFromColorValue(this.data.capital_color || "#ffffff");
    const strokeColor = luminance < 100 ? 0xf5f5f5 : 0x000000;
    const pts = this.createStarPoints(centerX, centerY, outerRadius, innerRadius, 5);

    this.capitalGraphic.poly(pts);
    this.capitalGraphic.fill(fillColor);
    this.capitalGraphic.stroke({
      color: strokeColor,
      width: 2,
      join: "round"
    });
  }

  setColor(color) {
    this.data.color = color;
    this.drawPolygon();
    this.refreshTextStyles();
  }

  setTroops(value) {
    this.data.troops = value;
    this.troopText.text = value != null ? String(value) : "";
  }

  setIcons(iconState = {}) {
    if ("devImg" in iconState) this.data.devImg = iconState.devImg;
    if ("insig" in iconState) this.data.insig = iconState.insig;
    if ("hallImg" in iconState) this.data.hallImg = iconState.hallImg;
    if ("leylineImg" in iconState) this.data.leylineImg = iconState.leylineImg;
    this.syncIcons();
  }
}

class PixiMapRenderer {
  constructor(options) {
    this.containerId = options.containerId;
    this.mapName = options.mapName;
    this.tnames = options.tnames || [];
    this.tneighbors = options.tneighbors || [];
    this.landlocked = options.landlocked || [];

    this.container = null;
    this.app = null;
    this.world = null;
    this.baseLayer = null;
    this.seaRouteLayer = null;
    this.contBorderLayer = null;
    this.overlayLayer = null;
    this.backgroundSprite = null;

    this.iconTextures = null;
    this.seaRouteDotsGraphics = null;
    this.seaRouteLinesGraphics = null;
    this.contBorderGraphics = null;
    this.contBonusBoxLayer = null;

    this.hoverOverlay = null;
    this.targetCaptureOverlay = null;
    this.otherHighlightOverlay = null;
    this.toHighlightOverlay = null;
    this.clickablesLayer = null;

    this.mapProperties = null;
    this.territories = [];
    this.seaRoutes = [];
    this.contBorders = [];
    this.contBonusBoxes = [];

    this.territoryViews = [];
    this.zoomThreshold = 0.4;
    this.viewMode = "near";

    this.hoveredTerritoryId = null;
    this.hoverPulseTime = 0;

    this.toHighLight = [];
    this.clickables = [];
    this.targetsToCapture = [];
    this.otherHighlight = [];

    this.toHighlightSet = new Set();
    this.clickablesSet = new Set();
    this.targetsToCaptureSet = new Set();
    this.otherHighlightSet = new Set();

    this.clickableIndicators = new Map();
    this.clickableAnimTime = 0;
    this.clickableMaxOffset = 18;
    this.clickableSpeed = 0.0028;

    this.showContBorders = false;

    this.dragging = false;
    this.dragMoved = false;
  }

  async init() {
    this.container = document.getElementById(this.containerId);
    if (!this.container) {
      throw new Error(`Container not found: ${this.containerId}`);
    }

    if (document.fonts && document.fonts.load) {
      await document.fonts.load('12px "Urbanist"');
      await document.fonts.load('16px "Urbanist"');
      await document.fonts.load('35px "Urbanist"');
    }

    this.app = new PIXI.Application();
    await this.app.init({
      resizeTo: this.container,
      antialias: true,
      background: 0x111111,
      resolution: Math.min(window.devicePixelRatio || 1, 2),
      autoDensity: true
    });

    this.container.innerHTML = "";
    this.container.appendChild(this.app.canvas);

    const bgTexture = await PIXI.Assets.load("/static/Assets/Background/background.svg");
    this.iconTextures = {
      city: await PIXI.Assets.load("/static/Assets/Dev/city.png"),
      megacity: await PIXI.Assets.load("/static/Assets/Dev/megacity.png"),
      nexus: await PIXI.Assets.load("/static/Assets/Dev/transhub.png"),
      fort: await PIXI.Assets.load("/static/Assets/Insig/fort.png"),
      hall: await PIXI.Assets.load("/static/Assets/Insig/CAD.png"),
      leyline: await PIXI.Assets.load("/static/Assets/Insig/leyline.png"),
      bureau: await PIXI.Assets.load("/static/Assets/Insig/mobbureau.png")
    };

    this.backgroundSprite = new PIXI.Sprite(bgTexture);
    this.backgroundSprite.x = 0;
    this.backgroundSprite.y = 0;
    this.backgroundSprite.width = this.app.screen.width;
    this.backgroundSprite.height = this.app.screen.height;
    this.app.stage.addChild(this.backgroundSprite);

    this.world = new PIXI.Container();
    this.baseLayer = new PIXI.Container();
    this.seaRouteLayer = new PIXI.Container();
    this.contBorderLayer = new PIXI.Container();
    this.overlayLayer = new PIXI.Container();

    this.hoverOverlay = new PIXI.Graphics();
    this.targetCaptureOverlay = new PIXI.Graphics();
    this.otherHighlightOverlay = new PIXI.Graphics();
    this.toHighlightOverlay = new PIXI.Graphics();
    this.clickablesLayer = new PIXI.Container();

    this.contBorderGraphics = new PIXI.Graphics();
    this.contBonusBoxLayer = new PIXI.Container();
    this.contBorderLayer.addChild(this.contBorderGraphics);
    this.contBorderLayer.addChild(this.contBonusBoxLayer);
    this.contBorderLayer.visible = false;

    this.world.roundPixels = true;
    this.baseLayer.roundPixels = true;
    this.seaRouteLayer.roundPixels = true;
    this.contBorderLayer.roundPixels = true;
    this.overlayLayer.roundPixels = true;
    this.hoverOverlay.roundPixels = true;
    this.targetCaptureOverlay.roundPixels = true;
    this.otherHighlightOverlay.roundPixels = true;
    this.toHighlightOverlay.roundPixels = true;
    this.clickablesLayer.roundPixels = true;

    this.overlayLayer.addChild(this.targetCaptureOverlay);
    this.overlayLayer.addChild(this.hoverOverlay);
    this.overlayLayer.addChild(this.clickablesLayer);
    this.overlayLayer.addChild(this.otherHighlightOverlay);
    this.overlayLayer.addChild(this.toHighlightOverlay);

    this.world.addChild(this.baseLayer);
    this.world.addChild(this.seaRouteLayer);
    this.world.addChild(this.overlayLayer);
    this.world.addChild(this.contBorderLayer);
    this.app.stage.addChild(this.world);

    this.app.renderer.on("resize", (width, height) => {
      if (this.backgroundSprite) {
        this.backgroundSprite.width = width;
        this.backgroundSprite.height = height;
      }
    });

    await this.loadMapComponents();
    this.buildMap();
    this.buildSeaRouteGraphics();
    this.buildContinentBorderGraphics();
    this.setupDragAndZoom();
    this.fitWorldToMap();
    this.updateViewModeFromZoom(true);
    this.refreshAllOverlays();

    this.app.ticker.add((ticker) => {
      this.updateHoverPulse(ticker.deltaMS);
      this.updateClickableAnimation(ticker.deltaMS);
    });
  }

  async loadJson(path) {
    const res = await fetch(path);
    if (!res.ok) {
      throw new Error(`Failed to load ${path}: ${res.status}`);
    }
    return await res.json();
  }

  async loadMapComponents() {
    const mapName = this.mapName;

    this.mapProperties = await this.loadJson(`/static/MAPS/${mapName}/properties.json`);

    const continentPromises = [];
    for (let i = 1; i <= this.mapProperties.numConts; i++) {
      continentPromises.push(this.loadContinentData(mapName, i));
    }

    const continentDataArray = await Promise.all(continentPromises);

    const landlockedSet = new Set(this.landlocked);
    let tIndex = 0;

    for (let c = 0; c < continentDataArray.length; c++) {
      const contData = continentDataArray[c];
      const {
        sr_per_trty,
        numt,
        polygons,
        srs,
        cps,
        nameSpaces,
        troopSpaces,
        capitalSpaces,
        devSpaces,
        insigSpaces
      } = contData;

      let seaSideCounter = 0;

      for (let i = 0; i < numt; i++) {
        const territoryName = this.tnames[tIndex] || `Territory ${tIndex}`;
        const isLandlocked = landlockedSet.has(territoryName);

        let srcs = [];
        if (!isLandlocked) {
          const startIdx = sr_per_trty * seaSideCounter;
          srcs = srs.slice(startIdx, startIdx + sr_per_trty);
          seaSideCounter++;
        }

        this.territories.push({
          id: tIndex,
          name: territoryName,
          neighbors: this.tneighbors[tIndex] || [],
          outline: polygons[i],
          srcs,
          cps: cps[i],
          ns: nameSpaces[i],
          ts: troopSpaces[i],
          cs: capitalSpaces[i],
          ds: devSpaces[i],
          is: insigSpaces[i],
          troops: "",
          color: "#ffffff",
          capital_color: null,
          isCapital: false,
          devImg: null,
          insig: null,
          hallImg: null,
          leylineImg: null
        });

        tIndex++;
      }
    }

    const extras = await Promise.allSettled([
      this.loadJson(`/static/MAPS/${this.mapName}/seaRoutes.json`),
      this.loadJson(`/static/MAPS/${this.mapName}/contBorders.json`),
      this.loadJson(`/static/MAPS/${this.mapName}/contBonusDisplay.json`)
    ]);

    if (extras[0].status === "fulfilled") this.seaRoutes = extras[0].value;
    if (extras[1].status === "fulfilled") this.contBorders = extras[1].value;
    if (extras[2].status === "fulfilled") this.contBonusBoxes = extras[2].value;
  }

  async loadContinentData(mapName, contNum) {
    const base = `/static/MAPS/${mapName}/C${contNum}`;

    const [
      props,
      polygons,
      srs,
      cps,
      nameSpaces,
      troopSpaces,
      capitalSpaces,
      devSpaces,
      insigSpaces
    ] = await Promise.all([
      this.loadJson(`${base}/properties.json`),
      this.loadJson(`${base}/c${contNum}a.json`),
      this.loadJson(`${base}/c${contNum}sr.json`),
      this.loadJson(`${base}/c${contNum}cp.json`),
      this.loadJson(`${base}/displaySections/c${contNum}ns.json`),
      this.loadJson(`${base}/displaySections/c${contNum}ts.json`),
      this.loadJson(`${base}/displaySections/c${contNum}cs.json`),
      this.loadJson(`${base}/displaySections/c${contNum}ds.json`),
      this.loadJson(`${base}/displaySections/c${contNum}is.json`)
    ]);

    return {
      sr_per_trty: props.numSrp,
      numt: props.numt,
      polygons,
      srs,
      cps,
      nameSpaces,
      troopSpaces,
      capitalSpaces,
      devSpaces,
      insigSpaces
    };
  }

  buildMap() {
    this.territoryViews = [];

    for (let i = 0; i < this.territories.length; i++) {
      const territory = this.territories[i];

      const view = new TerritoryView(territory, i, this.iconTextures, {
        onHover: (id) => {
          this.hoveredTerritoryId = id;
          this.drawHoverOverlay();
        },
        onOut: (id) => {
          if (this.hoveredTerritoryId === id) {
            this.hoveredTerritoryId = null;
            this.hoverOverlay.clear();
          }
        },
        onClick: (id) => {
          if (this.dragMoved) return;
          console.log("clicked territory:", id, this.territories[id]?.name);
        }
      });

      this.territoryViews.push(view);
      this.baseLayer.addChild(view.container);
    }
  }

  buildSeaRouteGraphics() {
    if (this.seaRouteDotsGraphics) {
      this.seaRouteLayer.removeChild(this.seaRouteDotsGraphics);
      this.seaRouteDotsGraphics.destroy();
      this.seaRouteDotsGraphics = null;
    }

    if (this.seaRouteLinesGraphics) {
      this.seaRouteLayer.removeChild(this.seaRouteLinesGraphics);
      this.seaRouteLinesGraphics.destroy();
      this.seaRouteLinesGraphics = null;
    }

    this.seaRouteLinesGraphics = new PIXI.Graphics();
    this.seaRouteDotsGraphics = new PIXI.Graphics();

    this.drawSeaRouteLines(this.seaRouteLinesGraphics);
    this.drawSeaRouteCoordinates(this.seaRouteDotsGraphics);

    this.seaRouteLayer.addChild(this.seaRouteLinesGraphics);
    this.seaRouteLayer.addChild(this.seaRouteDotsGraphics);
  }

  buildContinentBorderGraphics() {
    this.drawContinentBorders();
    this.drawContinentBonusBoxes();
    this.contBorderLayer.visible = this.showContBorders;
  }

  drawContinentBorders() {
    if (!this.contBorderGraphics) return;

    this.contBorderGraphics.clear();

    if (!this.contBorders || !this.contBorders.length) return;

    for (let i = 0; i < this.contBorders.length; i++) {
      const border = this.contBorders[i];
      if (!border || !border.length) continue;

      const pts = [];
      for (let j = 0; j < border.length; j++) {
        pts.push(border[j].x, border[j].y);
      }

      this.contBorderGraphics.poly(pts);
      this.contBorderGraphics.fill({
        color: 0x808080,
        alpha: 100 / 255
      });
      this.contBorderGraphics.stroke({
        color: 0x000000,
        width: 4,
        alpha: 1,
        join: "round"
      });
    }
  }

  drawContinentBonusBoxes() {
    if (!this.contBonusBoxLayer) return;

    this.contBonusBoxLayer.removeChildren();

    if (!this.contBonusBoxes || !this.contBonusBoxes.length) return;

    for (let i = 0; i < this.contBonusBoxes.length; i++) {
      const bonus = this.contBonusBoxes[i];
      if (!bonus) continue;

      const box = new PIXI.Container();
      box.roundPixels = true;

      const bg = new PIXI.Graphics();
      bg.rect(bonus.x, bonus.y, bonus.dx, bonus.dy);
      bg.fill(0xffffff);
      bg.stroke({
        color: 0x000000,
        width: 1,
        alpha: 1,
        join: "miter"
      });

      const text = new PIXI.Text({
        text: bonus.message || "",
        style: new PIXI.TextStyle({
          fontFamily: "Urbanist",
          fontSize: 15,
          fill: 0x000000,
          fontWeight: "700",
          align: "center"
        })
      });

      text.anchor.set(0.5);
      text.resolution = 2;
      text.roundPixels = true;
      text.x = Math.round(bonus.cx);
      text.y = Math.round(bonus.cy);

      box.addChild(bg);
      box.addChild(text);
      this.contBonusBoxLayer.addChild(box);
    }
  }

  drawSeaRouteCoordinates(gfx) {
    gfx.clear();

    const fillColor = 0x22d3ee;
    const radius = 5;

    for (let i = 0; i < this.territories.length; i++) {
      const trty = this.territories[i];
      if (!trty.srcs || !trty.srcs.length) continue;

      for (let j = 0; j < trty.srcs.length; j++) {
        const src = trty.srcs[j];
        gfx.circle(src.x, src.y, radius);
        gfx.fill(fillColor);
      }
    }
  }

  drawSeaRouteLines(gfx) {
    gfx.clear();

    const dotColor = 0xc8c8c8;
    const radius = 2.5;
    const dotSpacing = 6;

    for (let i = 0; i < this.seaRoutes.length; i++) {
      const route = this.seaRoutes[i];
      this.drawDottedRouteToGraphics(
        gfx,
        route.x1,
        route.y1,
        route.x2,
        route.y2,
        dotSpacing,
        radius,
        dotColor
      );
    }
  }

  drawDottedRouteToGraphics(gfx, x1, y1, x2, y2, dotSpacing = 6, radius = 2.5, color = 0xc8c8c8) {
    const dx = x2 - x1;
    const dy = y2 - y1;
    const lineLength = Math.sqrt(dx * dx + dy * dy);

    if (lineLength <= 0) {
      gfx.circle(x1, y1, radius);
      gfx.fill(color);
      return;
    }

    for (let i = 0; i <= lineLength; i += dotSpacing * 2) {
      const t = i / lineLength;
      const x = x1 + dx * t;
      const y = y1 + dy * t;
      gfx.circle(x, y, radius);
      gfx.fill(color);
    }
  }

  getTerritoryFlatPoints(id) {
    const trty = this.territories[id];
    if (!trty || !trty.outline || !trty.outline.length) return [];

    const pts = [];
    for (let i = 0; i < trty.outline.length; i++) {
      pts.push(trty.outline[i].x, trty.outline[i].y);
    }
    return pts;
  }

  getHighlightContrastColor(id) {
    const view = this.territoryViews[id];
    if (!view) return 0x000000;
    return view.isDarkFill() ? 0xf5f5f5 : 0x000000;
  }

  drawPolygonOutline(gfx, points, color, width, alpha = 1) {
    if (!points || !points.length) return;
    gfx.poly(points);
    gfx.stroke({
      color,
      width,
      alpha,
      join: "round"
    });
  }

  drawHoverOverlay() {
    this.hoverOverlay.clear();

    if (this.hoveredTerritoryId == null) return;

    const pts = this.getTerritoryFlatPoints(this.hoveredTerritoryId);
    if (!pts.length) return;

    const s = 1 + 0.3 * Math.sin(this.hoverPulseTime);
    const width = 2.5 * s;
    const alpha = 220 / 255;

    this.drawPolygonOutline(this.hoverOverlay, pts, 0xffffff, width, alpha);
  }

  updateHoverPulse(deltaMS) {
    if (this.hoveredTerritoryId == null) return;
    this.hoverPulseTime += deltaMS * 0.01;
    this.drawHoverOverlay();
  }

  refreshTargetsToCaptureOverlay() {
    this.targetCaptureOverlay.clear();

    for (const id of this.targetsToCaptureSet) {
      const pts = this.getTerritoryFlatPoints(id);
      if (!pts.length) continue;

      this.drawPolygonOutline(this.targetCaptureOverlay, pts, 0xffbf00, 7, 70 / 255);
      this.drawPolygonOutline(this.targetCaptureOverlay, pts, 0xffbf00, 4, 1);
    }
  }

  refreshOtherHighlightOverlay() {
    this.otherHighlightOverlay.clear();

    for (const id of this.otherHighlightSet) {
      const pts = this.getTerritoryFlatPoints(id);
      if (!pts.length) continue;

      this.drawPolygonOutline(this.otherHighlightOverlay, pts, 0x000000, 4, 1);
    }
  }

  refreshToHighlightOverlay() {
    this.toHighlightOverlay.clear();

    for (const id of this.toHighlightSet) {
      const pts = this.getTerritoryFlatPoints(id);
      if (!pts.length) continue;

      const color = this.getHighlightContrastColor(id);
      this.drawPolygonOutline(this.toHighlightOverlay, pts, color, 4, 1);
    }
  }

  createClickableIndicator(id) {
    const trty = this.territories[id];
    if (!trty || !trty.cps) return null;

    const g = new PIXI.Graphics();
    g.eventMode = "none";
    g.roundPixels = true;

    const halfBase = 10;
    const topY = -17.3205;
    const bottomY = 0;

    g.poly([
      -halfBase, topY,
       halfBase, topY,
       0,        bottomY
    ]);
    g.fill(0xff0000);
    g.stroke({
      color: 0x000000,
      width: 2,
      join: "round"
    });

    g.x = Math.round(trty.cps.x);
    g.y = Math.round(trty.cps.y);
    g.baseY = Math.round(trty.cps.y);

    this.clickablesLayer.addChild(g);
    return g;
  }

  refreshClickables() {
    const nextIds = this.clickablesSet;

    for (const [id, indicator] of this.clickableIndicators.entries()) {
      if (!nextIds.has(id)) {
        this.clickablesLayer.removeChild(indicator);
        indicator.destroy();
        this.clickableIndicators.delete(id);
      }
    }

    for (const id of nextIds) {
      if (!this.clickableIndicators.has(id)) {
        const indicator = this.createClickableIndicator(id);
        if (indicator) this.clickableIndicators.set(id, indicator);
      } else {
        const indicator = this.clickableIndicators.get(id);
        const trty = this.territories[id];
        if (indicator && trty && trty.cps) {
          indicator.x = Math.round(trty.cps.x);
          indicator.baseY = Math.round(trty.cps.y);
        }
      }
    }

    this.clickablesLayer.visible = this.clickablesSet.size > 0;
  }

  updateClickableAnimation(deltaMS) {
    if (this.clickableIndicators.size === 0) return;

    this.clickableAnimTime += deltaMS * this.clickableSpeed;

    const normalized = (Math.sin(this.clickableAnimTime) + 1) * 0.5;
    const offset = normalized * this.clickableMaxOffset;

    for (const indicator of this.clickableIndicators.values()) {
      indicator.y = Math.round(indicator.baseY + offset);
    }
  }

  refreshAllOverlays() {
    this.refreshTargetsToCaptureOverlay();
    this.refreshOtherHighlightOverlay();
    this.refreshToHighlightOverlay();
    this.refreshClickables();
    this.drawHoverOverlay();
  }

  normalizeIdArray(ids) {
    if (!Array.isArray(ids)) return [];

    const max = this.territories.length;
    const seen = new Set();
    const out = [];

    for (let i = 0; i < ids.length; i++) {
      const n = Number(ids[i]);
      if (!Number.isInteger(n)) continue;
      if (n < 0 || n >= max) continue;
      if (seen.has(n)) continue;
      seen.add(n);
      out.push(n);
    }

    return out;
  }

  setToHighLight(ids = []) {
    this.toHighLight = this.normalizeIdArray(ids);
    this.toHighlightSet = new Set(this.toHighLight);
    this.refreshToHighlightOverlay();
  }

  setClickables(ids = []) {
    this.clickables = this.normalizeIdArray(ids);
    this.clickablesSet = new Set(this.clickables);
    this.refreshClickables();
  }

  setTargetsToCapture(ids = []) {
    this.targetsToCapture = this.normalizeIdArray(ids);
    this.targetsToCaptureSet = new Set(this.targetsToCapture);
    this.refreshTargetsToCaptureOverlay();
  }

  setOtherHighlight(ids = []) {
    this.otherHighlight = this.normalizeIdArray(ids);
    this.otherHighlightSet = new Set(this.otherHighlight);
    this.refreshOtherHighlightOverlay();
  }

  setShowContBorders(value) {
    this.showContBorders = !!value;
    if (this.contBorderLayer) {
        this.contBorderLayer.visible = this.showContBorders;
        this.world.removeChild(this.contBorderLayer);
        this.world.addChild(this.contBorderLayer);
    }
  }

  toggleContBorders() {
    this.setShowContBorders(!this.showContBorders);
  }

  clearToHighLight() {
    this.setToHighLight([]);
  }

  clearClickables() {
    this.setClickables([]);
  }

  clearTargetsToCapture() {
    this.setTargetsToCapture([]);
  }

  clearOtherHighlight() {
    this.setOtherHighlight([]);
  }

  getMapBounds() {
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;

    for (let i = 0; i < this.territories.length; i++) {
      const outline = this.territories[i].outline || [];
      for (let j = 0; j < outline.length; j++) {
        const p = outline[j];
        if (p.x < minX) minX = p.x;
        if (p.y < minY) minY = p.y;
        if (p.x > maxX) maxX = p.x;
        if (p.y > maxY) maxY = p.y;
      }
    }

    if (!isFinite(minX)) {
      minX = 0;
      minY = 0;
      maxX = 100;
      maxY = 100;
    }

    return { minX, minY, maxX, maxY };
  }

  fitWorldToMap() {
    const bounds = this.getMapBounds();
    const mapWidth = bounds.maxX - bounds.minX;
    const mapHeight = bounds.maxY - bounds.minY;

    const scaleX = this.app.screen.width / Math.max(mapWidth, 1);
    const scaleY = this.app.screen.height / Math.max(mapHeight, 1);
    const scale = Math.min(scaleX, scaleY) * 0.98;

    this.world.scale.set(scale);

    this.world.x =
      this.app.screen.width / 2 - (bounds.minX + mapWidth / 2) * scale;

    this.world.y =
      this.app.screen.height / 2 - (bounds.minY + mapHeight / 2) * scale;
  }

  setupDragAndZoom() {
    let dragStart = null;
    let worldStart = null;

    this.app.stage.eventMode = "static";
    this.app.stage.hitArea = this.app.screen;

    this.app.stage.on("pointerdown", (e) => {
      this.dragging = true;
      this.dragMoved = false;
      dragStart = e.global.clone();
      worldStart = new PIXI.Point(this.world.x, this.world.y);
    });

    this.app.stage.on("pointerup", () => {
      this.dragging = false;
      requestAnimationFrame(() => {
        this.dragMoved = false;
      });
    });

    this.app.stage.on("pointerupoutside", () => {
      this.dragging = false;
      requestAnimationFrame(() => {
        this.dragMoved = false;
      });
    });

    this.app.stage.on("pointermove", (e) => {
      if (!this.dragging) return;

      const dx = e.global.x - dragStart.x;
      const dy = e.global.y - dragStart.y;

      if (Math.abs(dx) > 2 || Math.abs(dy) > 2) {
        this.dragMoved = true;
      }

      this.world.x = worldStart.x + dx;
      this.world.y = worldStart.y + dy;
    });

    this.app.canvas.addEventListener("wheel", (e) => {
      e.preventDefault();

      const oldScale = this.world.scale.x;
      const factor = e.deltaY < 0 ? 1.1 : 0.9;
      const newScale = Math.max(0.08, Math.min(6, oldScale * factor));

      const mouse = new PIXI.Point(e.offsetX, e.offsetY);
      const worldPosBefore = this.world.toLocal(mouse);

      this.world.scale.set(newScale);

      const screenPosAfter = this.world.toGlobal(worldPosBefore);
      this.world.x += mouse.x - screenPosAfter.x;
      this.world.y += mouse.y - screenPosAfter.y;

      this.updateViewModeFromZoom(false);
    }, { passive: false });
  }

  updateViewModeFromZoom(force = false) {
    const scale = this.world.scale.x;
    const nextMode = scale < this.zoomThreshold ? "far" : "near";

    if (!force && nextMode === this.viewMode) return;

    this.viewMode = nextMode;

    for (let i = 0; i < this.territoryViews.length; i++) {
      this.territoryViews[i].layoutForMode(this.viewMode);
    }
  }

  setTerritoryColor(id, color) {
    const view = this.territoryViews[id];
    if (!view) return;

    view.setColor(color);

    if (this.toHighlightSet.has(id)) {
      this.refreshToHighlightOverlay();
    }
  }

  setTerritoryTroops(id, troops) {
    const view = this.territoryViews[id];
    if (!view) return;
    view.setTroops(troops);
  }

  setTerritoryIcons(id, iconState) {
    const view = this.territoryViews[id];
    if (!view) return;
    view.setIcons(iconState);
  }

  setTerritoryCapital(id, capitalState) {
    const view = this.territoryViews[id];
    if (!view) return;
    view.setCapitalState(capitalState);
  }
}

window.PixiMapRenderer = PixiMapRenderer;