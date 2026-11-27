import React from "react";
import { expect, it } from "vitest";
import { pointFrom, type LocalPoint } from "@excalidraw/math";
import { Excalidraw } from "../index";
import { API } from "./helpers/api";
import { fireEvent, mockBoundingClientRect, render, restoreOriginalGetBoundingClientRect } from "./test-utils";

it.each([false, true])("observes one crossing drag (off-path control: %s)", async offPath => {
  mockBoundingClientRect({ width: 800, height: 600 });
  try {
    const view = await render(<Excalidraw />);
    const { app, state } = window.h;
    expect([state.zoom.value, state.scrollX, state.scrollY, state.offsetLeft, state.offsetTop])
      .toEqual([1, 0, 0, 0, 0]);
    const inputs = [{ id: "ordinary", y: 100, locked: false }, { id: "locked", y: 115, locked: true }];
    if (offPath) inputs.push({ id: "off-path", y: 190, locked: false });
    const arrows = inputs.map(({ id, y, locked }) => API.createElement({
      type: "arrow", id, locked, x: 100, y,
      width: 120, height: 0, strokeWidth: 2, roughness: 0, angle: 0, endArrowhead: "arrow",
      points: [pointFrom<LocalPoint>(0, 0), pointFrom<LocalPoint>(120, 0)],
    }));
    API.setElements(arrows);
    fireEvent.click(view.getByToolName("eraser"));
    expect(window.h.state.activeTool.type).toBe("eraser");
    expect(app.visibleElements.map(el => [el.id, el.locked, el.isDeleted]))
      .toEqual(inputs.map(el => [el.id, el.locked, false]));
    const canvas = view.container.querySelector("canvas.interactive")!;
    const pointer = (clientY: number, pressed: boolean) => ({
      pointerId: 1, pointerType: "mouse", button: 0, clientX: 160, clientY,
      buttons: pressed ? 1 : 0, pressure: pressed ? 0.5 : 0, altKey: false,
    });
    fireEvent.pointerDown(canvas, pointer(70, true));
    fireEvent.pointerMove(canvas, pointer(140, true));
    fireEvent.pointerUp(canvas, pointer(140, false));
    const result = app.scene.getElementsIncludingDeleted().map(el => ({
      id: el.id, deleted: el.isDeleted, live: app.scene.getNonDeletedElements().some(other => other.id === el.id),
    }));
    expect(result.map(el => el.id)).toEqual(inputs.map(el => el.id));
    for (const el of result) expect(el.live).toBe(!el.deleted);
    expect(result[1].live).toBe(true);
    if (offPath) expect(result[2].live).toBe(true);
    console.log("ARROW_SCENE", JSON.stringify(result));
  } finally {
    restoreOriginalGetBoundingClientRect();
  }
});
