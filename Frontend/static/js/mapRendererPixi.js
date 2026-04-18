class TerritoryView {
  constructor(data, id, callbacks = {}) {
    this.data = data;
    this.id = id;
    this.onHover = callbacks.onHover || null;
    this.onOut = callbacks.onOut || null;
    this.onClick = callbacks.onClick || null;
    this.viewMode = "near";

    this.container = new PIXI.Container();

    this.base = new PIXI.Graphics();
    this.border = new PIXI.Graphics();
    this.hover = new PIXI.Graphics();
    this.hit = new PIXI.Graphics();

    const textFill = this.getTextFill();

    this.nameStyle = new PIXI.TextStyle({
      fontFamily: "Urbanist",
      fontSize: 12,
      fill: textFill,
      fontWeight: "700",
      align: "left"
    });

    this.troopNearStyle = new PIXI.TextStyle({
      fontFamily: "Urbanist",
      fontSize: 16,
      fill: textFill,
      fontWeight: "700",
      align: "left"
    });

    this.troopFarStyle = new PIXI.TextStyle({
      fontFamily: "Urbanist",
      fontSize: 35,
      fill: textFill,
      fontWeight: "700",
      align: "left"
    });

    this.nameText = new PIXI.Text({
      text: this.data.name || "",
      style: this.nameStyle
    });

    this.troopText = new PIXI.Text({
      text: this.data.troops != null ? String(this.data.troops) : "",
      style: this.troopNearStyle
    });

    const textRes = 2;
    this.nameText.resolution = textRes;
    this.troopText.resolution = textRes;
    this.nameText.roundPixels = true;
    this.troopText.roundPixels = true;

    this.hover.visible = false;

    this.container.addChild(this.base);
    this.container.addChild(this.border);
    this.container.addChild(this.hover);
    this.container.addChild(this.hit);
    this.container.addChild(this.nameText);
    this.container.addChild(this.troopText);

    this.draw();
    this.makeInteractive();
    this.applyViewMode("near");
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
      if (colorValue.startsWith("#")) {
        return parseInt(colorValue.slice(1), 16);
      }

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

  isDarkFill() {
    const c = this.toPixiColor(this.data.color || "#ffffff");
    const r = (c >> 16) & 255;
    const g = (c >> 8) & 255;
    const b = c & 255;
    const brightness = (0.299 * r) + (0.587 * g) + (0.114 * b);
    return brightness < 128;
  }

  getTextFill() {
    return this.isDarkFill() ? 0xf5f5f5 : 0x000000;
  }

  updateTextFill() {
    const fill = this.getTextFill();
    this.nameStyle.fill = fill;
    this.troopNearStyle.fill = fill;
    this.troopFarStyle.fill = fill;
  }

  draw() {
    const pts = this.getFlatPoints();
    const fillColor = this.toPixiColor(this.data.color || "#ffffff");

    this.base.clear();
    this.base.poly(pts);
    this.base.fill(fillColor);

    this.border.clear();
    this.border.poly(pts);
    this.border.stroke({
      color: 0x666666,
      width: 1.5
    });

    this.hover.clear();
    this.hover.poly(pts);
    this.hover.stroke({
      color: 0xffffff,
      width: 4
    });

    this.hit.clear();
    this.hit.poly(pts);
    this.hit.fill({
      color: 0xffffff,
      alpha: 0.001
    });

    this.updateTextFill();
  }

  layoutNear() {
    if (this.data.ns) {
      this.nameText.position.set(Math.round(this.data.ns.x), Math.round(this.data.ns.y - 12));
    }

    if (this.data.ts) {
      this.troopText.position.set(Math.round(this.data.ts.x), Math.round(this.data.ts.y - 16));
    }
  }

  layoutFar() {
    if (this.data.cps) {
      this.troopText.position.set(Math.round(this.data.cps.x), Math.round(this.data.cps.y - 35));
    }
  }

  makeInteractive() {
    const pts = this.getFlatPoints();

    this.hit.eventMode = "static";
    this.hit.cursor = "pointer";
    this.hit.hitArea = new PIXI.Polygon(pts);

    this.hit.on("pointerover", () => {
      this.hover.visible = true;
      if (this.onHover) this.onHover(this.id);
    });

    this.hit.on("pointerout", () => {
      this.hover.visible = false;
      if (this.onOut) this.onOut(this.id);
    });

    this.hit.on("pointertap", () => {
      if (this.onClick) this.onClick(this.id);
    });
  }

  setColor(color) {
    this.data.color = color;
    this.draw();
  }

  setTroops(value) {
    this.data.troops = value;
    this.troopText.text = value != null ? String(value) : "";
  }

  applyViewMode(mode) {
    this.viewMode = mode;

    if (mode === "far") {
      this.nameText.visible = false;
      this.troopText.visible = true;
      if (this.troopText.style !== this.troopFarStyle) {
        this.troopText.style = this.troopFarStyle;
      }
      this.layoutFar();
      return;
    }

    this.nameText.visible = true;
    this.troopText.visible = true;
    if (this.troopText.style !== this.troopNearStyle) {
      this.troopText.style = this.troopNearStyle;
    }
    this.layoutNear();
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
    this.backgroundSprite = null;

    this.mapProperties = null;
    this.territories = [];
    this.seaRoutes = [];
    this.contBorders = [];
    this.contBonusBoxes = [];

    this.territoryViews = [];
    this.zoomThreshold = 0.4;
    this.viewMode = "near";
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

    const bgTexture = await PIXI.Assets.load('/static/Assets/Background/background.svg');
    this.backgroundSprite = new PIXI.Sprite(bgTexture);
    this.backgroundSprite.x = 0;
    this.backgroundSprite.y = 0;
    this.backgroundSprite.width = this.app.screen.width;
    this.backgroundSprite.height = this.app.screen.height;
    this.app.stage.addChild(this.backgroundSprite);

    this.world = new PIXI.Container();
    this.baseLayer = new PIXI.Container();

    this.world.roundPixels = true;
    this.baseLayer.roundPixels = true;

    this.world.addChild(this.baseLayer);
    this.app.stage.addChild(this.world);

    this.app.renderer.on("resize", (width, height) => {
      if (this.backgroundSprite) {
        this.backgroundSprite.width = width;
        this.backgroundSprite.height = height;
      }
    });

    await this.loadMapComponents();
    this.buildMap();
    this.setupDragAndZoom();
    this.fitWorldToMap();
    this.updateViewModeFromZoom(true);
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
          troops: "1",
          color: "#ffffff",
          capital_color: "#ffffff",
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

    console.log("Pixi map loaded:", {
      mapName: this.mapName,
      territories: this.territories.length,
      seaRoutes: this.seaRoutes.length
    });
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

      const view = new TerritoryView(territory, i, {
        onHover: () => {},
        onOut: () => {},
        onClick: (id) => {
          console.log("clicked territory:", id, this.territories[id]?.name);
        }
      });

      this.territoryViews.push(view);
      this.baseLayer.addChild(view.container);
    }
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
    let dragging = false;
    let dragStart = null;
    let worldStart = null;

    this.app.stage.eventMode = "static";
    this.app.stage.hitArea = this.app.screen;

    this.app.stage.on("pointerdown", (e) => {
      dragging = true;
      dragStart = e.global.clone();
      worldStart = new PIXI.Point(this.world.x, this.world.y);
    });

    this.app.stage.on("pointerup", () => {
      dragging = false;
    });

    this.app.stage.on("pointerupoutside", () => {
      dragging = false;
    });

    this.app.stage.on("pointermove", (e) => {
      if (!dragging) return;
      this.world.x = worldStart.x + (e.global.x - dragStart.x);
      this.world.y = worldStart.y + (e.global.y - dragStart.y);
    });

    this.app.canvas.addEventListener(
      "wheel",
      (e) => {
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
      },
      { passive: false }
    );
  }

  updateViewModeFromZoom(force = false) {
    const scale = this.world.scale.x;
    const nextMode = scale < this.zoomThreshold ? "far" : "near";

    if (!force && nextMode === this.viewMode) return;

    this.viewMode = nextMode;

    for (let i = 0; i < this.territoryViews.length; i++) {
      this.territoryViews[i].applyViewMode(this.viewMode);
    }
  }

  setTerritoryColor(id, color) {
    const view = this.territoryViews[id];
    if (!view) return;
    view.setColor(color);
  }

  setTerritoryTroops(id, troops) {
    const view = this.territoryViews[id];
    if (!view) return;
    view.setTroops(troops);
  }
}

window.PixiMapRenderer = PixiMapRenderer;