# -*- coding: utf-8 -*-
"""
Author: Juliette Monsel
License: GNU GPLv3
Source: This repository

Treeview with checkboxes at each item and a noticeable disabled style
"""

from tkinter import ttk
import sv_ttk

import os
import keyboard
from PIL import Image, ImageTk

import gui_elements
import tools
import json

IM_CHECKED_LIGHT_FOCUS = os.path.join("assets/light/check-focus.png")
IM_CHECKED_LIGHT_PRESSED = os.path.join("assets/light/check-pressed.png")
IM_CHECKED_LIGHT_REST = os.path.join("assets/light/check-rest.png")

IM_UNCHECKED_LIGHT_FOCUS = os.path.join("assets/light/check-unsel-focus.png")
IM_UNCHECKED_LIGHT_PRESSED = os.path.join("assets/light/check-unsel-pressed.png")
IM_UNCHECKED_LIGHT_REST = os.path.join("assets/light/check-unsel-rest.png")

IM_TRISTATE_LIGHT_FOCUS = os.path.join("assets/light/check-tri-focus.png")
IM_TRISTATE_LIGHT_PRESSED = os.path.join("assets/light/check-tri-pressed.png")
IM_TRISTATE_LIGHT_REST = os.path.join("assets/light/check-tri-rest.png")


IM_CHECKED_DARK_FOCUS = os.path.join("assets/dark/check-focus.png")
IM_CHECKED_DARK_PRESSED = os.path.join("assets/dark/check-pressed.png")
IM_CHECKED_DARK_REST = os.path.join("assets/dark/check-rest.png")

IM_UNCHECKED_DARK_FOCUS = os.path.join("assets/dark/check-unsel-focus.png")
IM_UNCHECKED_DARK_PRESSED = os.path.join("assets/dark/check-unsel-pressed.png")
IM_UNCHECKED_DARK_REST = os.path.join("assets/dark/check-unsel-rest.png")

IM_TRISTATE_DARK_FOCUS = os.path.join("assets/dark/check-tri-focus.png")
IM_TRISTATE_DARK_PRESSED = os.path.join("assets/dark/check-tri-pressed.png")
IM_TRISTATE_DARK_REST = os.path.join("assets/dark/check-tri-rest.png")


class CheckboxTreeview(ttk.Treeview):
    """
    :class:`ttk.Treeview` widget with checkboxes left of each item.

    .. note::
        The checkboxes are done via the image attribute of the item,
        so to keep the checkbox, you cannot add an image to the item.
    """

    def __init__(self, master=None, **kw):
        """
        Create a CheckboxTreeview.

        :param master: master widget
        :type master: widget
        :param kw: options to be passed on to the :class:`ttk.Treeview` initializer
        """
        self.current_selection = []
        self.previous_item_selected = [0, False]
        self.item_selected = 0
        ttk.Treeview.__init__(self, master, style='Checkbox.Treeview', **kw)
        # checkboxes are implemented with pictures
        self.update_theme()
        # check / uncheck boxes on click
        self.bind("<Button-1>", self._box_pressed, True)
        self.bind("<ButtonRelease-1>", self._box_click, True)

    def expand_all(self):
        """Expand all items."""

        def aux(item):
            self.item(item, open=True)
            children = self.get_children(item)
            for c in children:
                aux(c)

        children = self.get_children("")
        for c in children:
            aux(c)

    def collapse_all(self):
        """Collapse all items."""

        def aux(item):
            self.item(item, open=False)
            children = self.get_children(item)
            for c in children:
                aux(c)

        children = self.get_children("")
        for c in children:
            aux(c)

    def state(self, statespec=None):
        """
        Modify or inquire widget state.

        :param statespec: Widget state is returned if `statespec` is None,
                          otherwise it is set according to the statespec
                          flags and then a new state spec is returned
                          indicating which flags were changed.
        :type statespec: None or sequence[str]
        """
        if statespec:
            if "disabled" in statespec:
                self.bind('<ButtonRelease-1>', lambda e: 'break')
            elif "!disabled" in statespec:
                self.unbind("<ButtonRelease-1>")
                self.bind("<ButtonRelease-1>", self._box_click, True)
            return ttk.Treeview.state(self, statespec)
        else:
            return ttk.Treeview.state(self)

    def change_state(self, item, state):
        """
        Replace the current state of the item.

        i.e. replace the current state tag but keeps the other tags.

        :param item: item id
        :type item: str
        :param state: "checked", "unchecked" or "tristate": new state of the item
        :type state: str
        """
        tags = self.item(item, "tags")
        states = ("checked", "unchecked", "tristate", "checked_pressed", "unchecked_pressed", "tristate_pressed", "checked_focus", "unchecked_focus", "tristate_focus")
        new_tags = [t for t in tags if t not in states]
        new_tags.append(state)
        self.item(item, tags=tuple(new_tags))

    def tag_add(self, item, tag):
        """
        Add tag to the tags of item.

        :param item: item identifier
        :type item: str
        :param tag: tag name
        :type tag: str
        """
        tags = self.item(item, "tags")
        self.item(item, tags=tags + (tag,))

    def tag_del(self, item, tag):
        """
        Remove tag from the tags of item.

        :param item: item identifier
        :type item: str
        :param tag: tag name
        :type tag: str
        """
        tags = list(self.item(item, "tags"))
        if tag in tags:
            tags.remove(tag)
            self.item(item, tags=tuple(tags))

    def insert(self, parent, index, iid=None, **kw):
        """
        Creates a new item and return the item identifier of the newly created item.

        :param parent: identifier of the parent item
        :type parent: str
        :param index: where in the list of parent's children to insert the new item
        :type index: int or "end"
        :param iid: item identifier, iid must not already exist in the tree. If iid is None a new unique identifier is generated.
        :type iid: None or str
        :param kw: other options to be passed on to the :meth:`ttk.Treeview.insert` method

        :return: the item identifier of the newly created item
        :rtype: str

        .. note:: Same method as for the standard :class:`ttk.Treeview` but
                  add the tag for the box state accordingly to the parent
                  state if no tag among
                  ('checked', 'unchecked', 'tristate') is given.
        """
        if self.tag_has("checked", parent):
            tag = "checked"
        else:
            tag = 'unchecked'
        if "tags" not in kw:
            kw["tags"] = (tag,)
        elif not ("unchecked" in kw["tags"] or "checked" in kw["tags"] or
                  "tristate" in kw["tags"]):
            kw["tags"] += (tag,)

        return ttk.Treeview.insert(self, parent, index, iid, **kw)

    def set_selection(self, *items):
        self.selection_set(items)
        self.focus_selection(items)

    def get_checked(self):
        """Return the list of checked items that do not have any child."""
        checked = []

        def get_checked_children(item):
            if not self.tag_has("unchecked", item):
                ch = self.get_children(item)
                if not ch and (self.tag_has("checked", item) or self.tag_has("checked_focus", item)):
                    checked.append(item)
                else:
                    for c in ch:
                        get_checked_children(c)

        ch = self.get_children("")
        for c in ch:
            get_checked_children(c)
        return checked

    def get_checked_name(self):
        """Return the list of checked items name that do not have any child."""
        checked_name = []

        def get_checked_name_children(item):
            if not self.tag_has("unchecked", item):
                ch = self.get_children(item)
                if not ch and (self.tag_has("checked", item) or self.tag_has("checked_focus", item)):
                    checked_name.append(self.item(item, "text"))
                else:
                    for c in ch:
                        get_checked_name_children(c)

        ch = self.get_children("")
        for c in ch:
            get_checked_name_children(c)
        return checked_name

    def get_item_iid(self, name):
        for iid in self.get_children("0"):
            if self.item(iid, "text") == name:
                return iid

    def _check_descendant(self, item):
        """Check the boxes of item's descendants."""
        children = self.get_children(item)
        for iid in children:
            self.change_state(iid, "checked")
            self._check_descendant(iid)

    def _check_ancestor(self, item):
        """
        Check the box of item and change the state of the boxes of item's
        ancestors accordingly.
        """
        self.change_state(item, "checked")
        parent = self.parent(item)
        if parent:
            children = self.get_children(parent)
            b = ["checked" in self.item(c, "tags") or "checked_focus" in self.item(c, "tags") for c in children]
            if False in b:
                # at least one box is not checked and item's box is checked
                self._tristate_parent(parent)
            else:
                # all boxes of the children are checked
                self._check_ancestor(parent)

    def _tristate_parent(self, item):
        """
        Put the box of item in tristate and change the state of the boxes of
        item's ancestors accordingly.
        """
        self.change_state(item, "tristate")
        parent = self.parent(item)
        if parent:
            self._tristate_parent(parent)

    def _uncheck_descendant(self, item):
        """Uncheck the boxes of item's descendant."""
        children = self.get_children(item)
        for iid in children:
            self.change_state(iid, "unchecked")
            self._uncheck_descendant(iid)

    def _uncheck_ancestor(self, item):
        """
        Uncheck the box of item and change the state of the boxes of item's
        ancestors accordingly.
        """
        self.change_state(item, "unchecked")
        parent = self.parent(item)
        if parent:
            children = self.get_children(parent)
            b = [("unchecked" in self.item(c, "tags") or ("unchecked_focus" in self.item(c, "tags"))) for c in children]
            if False in b:
                # at least one box is checked and item's box is unchecked
                self._tristate_parent(parent)
            else:
                # no box is checked
                self._uncheck_ancestor(parent)

    def _get_tree_items(self):
        items = []
        for parent in self.get_children():
            items.append(parent)
            for child in self.get_children(parent):
                items.append(child)
        return items

    def _update_selection(self, item):
        item = int(item)
        prev_item = self.previous_item_selected
        int_prev_item = int(prev_item[0])
        items = []

        if keyboard.is_pressed("shift"):

            if not prev_item[1]:
                self.previous_item_selected[0] = self.item_selected
                self.previous_item_selected[1] = True
                prev_item = self.previous_item_selected
                int_prev_item = int(prev_item[0])

            if int_prev_item < item:
                for iid in self._get_tree_items():
                    if item >= int(iid) >= int_prev_item:
                        items.append(iid)
            elif int_prev_item > item:
                for iid in self._get_tree_items():
                    if item <= int(iid) <= int_prev_item:
                        items.append(iid)
            else:
                for iid in self._get_tree_items():
                    if int(iid) >= item:
                        items.append(iid)

            if self._is_selection_checked(items) and self._items_equal_sel(items, self.current_selection):
                self.uncheck_selection(items)
                self._uncheck_descendant(self.item_selected)
                self._uncheck_ancestor(self.item_selected)
            else:
                self._check_selection(items)
                self._check_ancestor(self.item_selected)
                self._check_descendant(self.item_selected)

            self._unfocus_all(items)
            self.focus_selection(items)
        else:
            self.previous_item_selected[0] = self.item_selected
            self.previous_item_selected[1] = False
            self.item_selected = item
            items.append(item)
            self._unfocus_all(items)
            self.focus_selection(items)

            self._press_item(item)

        return items

    def _is_selection_checked(self, sel):
        for iid in sel:
            if not self.tag_has("checked_focus", iid):
                return False
        return True

    def _unpress_all(self, selection):
        for iid in self._get_tree_items():
            if iid not in selection:
                if self.tag_has("unchecked_pressed", iid):
                    self.change_state(iid, "unchecked")
                elif self.tag_has("tristate_pressed", iid):
                    self.change_state(iid, "tristate")
                elif self.tag_has("checked_pressed", iid):
                    self.change_state(iid, "checked")

    def _unfocus_all(self, selection):
        for iid in self._get_tree_items():
            if iid not in selection:
                if self.tag_has("unchecked_focus", iid):
                    self.change_state(iid, "unchecked")
                elif self.tag_has("tristate_focus", iid):
                    self.change_state(iid, "tristate")
                elif self.tag_has("checked_focus", iid):
                    self.change_state(iid, "checked")

    def uncheck_all(self, selection):
        for iid in self._get_tree_items():
            if iid not in selection:
                if self.tag_has("tristate", iid):
                    self.change_state(iid, "unchecked")
                elif self.tag_has("tristate_focus", iid):
                    self.change_state(iid, "unchecked_focus")
                elif self.tag_has("checked", iid):
                    self.change_state(iid, "unchecked")
                elif self.tag_has("checked_focus", iid):
                    self.change_state(iid, "unchecked_focus")

    def uncheck_selection(self, selection):
        for iid in self._get_tree_items():
            if iid in selection:
                if self.tag_has("tristate", iid):
                    self.change_state(iid, "unchecked")
                elif self.tag_has("tristate_focus", iid):
                    self.change_state(iid, "unchecked_focus")
                elif self.tag_has("checked", iid):
                    self.change_state(iid, "unchecked")
                elif self.tag_has("checked_focus", iid):
                    self.change_state(iid, "unchecked_focus")

    def check_selection(self, selection):
        for iid in self._get_tree_items():
            if iid in selection:
                if self.tag_has("tristate", iid):
                    self.change_state(iid, "checked")
                elif self.tag_has("tristate_focus", iid):
                    self.change_state(iid, "checked_focus")
                elif self.tag_has("unchecked", iid):
                    self.change_state(iid, "unchecked")
                elif self.tag_has("unchecked_focus", iid):
                    self.change_state(iid, "checked_focus")

    def check_only_selection(self, selection):
        self.uncheck_all([])
        self.check_selection_name(selection)

    def check_selection_name(self, selection):
        for iid in self._get_tree_items():
            if self.item(iid, "text") in selection:
                self._check_ancestor(iid)
                self._check_descendant(iid)
        self.focus_selection(self.selection())

    def uncheck_selection_name(self, selection):
        for iid in self._get_tree_items():
            if self.item(iid, "text") in selection:
                self._uncheck_descendant(iid)
                self._uncheck_ancestor(iid)
        self.focus_selection(self.selection())

    def _check_selection(self, selection):
        for iid in self._get_tree_items():
            if iid in selection:
                self.change_state(iid, "checked_focus")

    def _press_item(self, item):
        if self.tag_has("unchecked", item) or self.tag_has("unchecked_focus", item):
            self.change_state(item, "unchecked_pressed")
        elif self.tag_has("tristate", item) or self.tag_has("tristate_focus", item):
            self.change_state(item, "tristate_pressed")
        else:
            self.change_state(item, "checked_pressed")

    def focus_selection(self, selection):
        for iid in selection:
            if self.tag_has("unchecked", iid):
                self.change_state(iid, "unchecked_focus")
            elif self.tag_has("tristate", iid):
                self.change_state(iid, "tristate_focus")
            elif not (self.tag_has("unchecked_focus", iid) or self.tag_has("tristate_focus", iid)):
                self.change_state(iid, "checked_focus")

    def _items_equal_sel(self, items, sel):
        if not len(items) == len(sel):
            return False
        for item in items:
            if item not in sel:
                return False
        return True

    def _box_pressed(self, event):
        """Check or uncheck box when clicked."""
        x, y, widget = event.x, event.y, event.widget
        item = self.identify_row(y)
        if item != "":
            items = self._update_selection(item)
            self.current_selection = items

    def _box_click(self, event):
        """Check or uncheck box when clicked."""
        x, y, widget = event.x, event.y, event.widget
        item = self.identify_row(y)
        if not keyboard.is_pressed("shift") and item != "":
            if self.tag_has("unchecked_pressed", str(self.item_selected)) or self.tag_has("tristate_pressed", str(self.item_selected)):
                self._check_ancestor(self.item_selected)
                self._check_descendant(self.item_selected)
            else:
                self._uncheck_descendant(self.item_selected)
                self._uncheck_ancestor(self.item_selected)
            self.focus_selection(self.selection())
            if gui_elements.get_mods_list_tree() is not None and gui_elements.get_mods_list_tree() is self:
                if not (self.tag_has("checked", str(self.item_selected)) or self.tag_has("checked_focus", str(self.item_selected))):
                    self.uncheck_mods_tree(item)
                self.check_mods_tree()

    def get_mods_selection_iid(self, iid, directory):
        selection = []
        mods = json.loads(open(f'{directory}\{self.item(iid, "text")}', "r").read())
        for mod in mods:
            selection.append(mod)
        return selection

    def get_mods_selection(self, item=None):
        directory = tools.get_mods_list_directory()
        if not tools.check_directory(directory):
            return

        if item is not None:
            return self.get_mods_selection_iid(item, directory)

        selection = []
        for iid in self.get_children():
            if self.tag_has("checked", iid) or self.tag_has("checked_focus", iid):
                selection += self.get_mods_selection_iid(iid, directory)
        return selection

    def uncheck_mods_tree(self, item):
        selection = self.get_mods_selection(item)
        gui_elements.get_mods_tree().uncheck_selection_name(selection)

    def check_mods_tree(self):
        selection = self.get_mods_selection()
        gui_elements.get_mods_tree().check_selection_name(selection)

    def check_uncheck_tree(self):
        self.uncheck_mods_tree(None)
        self.check_mods_tree()

    def update_theme(self):
        if sv_ttk.get_theme() == "dark":
            self.im_checked_focus = ImageTk.PhotoImage(Image.open(IM_CHECKED_DARK_FOCUS), master=self)
            self.im_checked_pressed = ImageTk.PhotoImage(Image.open(IM_CHECKED_DARK_PRESSED), master=self)
            self.im_checked_rest = ImageTk.PhotoImage(Image.open(IM_CHECKED_DARK_REST), master=self)

            self.im_unchecked_focus = ImageTk.PhotoImage(Image.open(IM_UNCHECKED_DARK_FOCUS), master=self)
            self.im_unchecked_pressed = ImageTk.PhotoImage(Image.open(IM_UNCHECKED_DARK_PRESSED), master=self)
            self.im_unchecked_rest = ImageTk.PhotoImage(Image.open(IM_UNCHECKED_DARK_REST), master=self)

            self.im_tristate_focus = ImageTk.PhotoImage(Image.open(IM_TRISTATE_DARK_FOCUS), master=self)
            self.im_tristate_pressed = ImageTk.PhotoImage(Image.open(IM_TRISTATE_DARK_PRESSED), master=self)
            self.im_tristate_rest = ImageTk.PhotoImage(Image.open(IM_TRISTATE_DARK_REST), master=self)
        else:
            self.im_checked_focus = ImageTk.PhotoImage(Image.open(IM_CHECKED_LIGHT_FOCUS), master=self)
            self.im_checked_pressed = ImageTk.PhotoImage(Image.open(IM_CHECKED_LIGHT_PRESSED), master=self)
            self.im_checked_rest = ImageTk.PhotoImage(Image.open(IM_CHECKED_LIGHT_REST), master=self)

            self.im_unchecked_focus = ImageTk.PhotoImage(Image.open(IM_UNCHECKED_LIGHT_FOCUS), master=self)
            self.im_unchecked_pressed = ImageTk.PhotoImage(Image.open(IM_UNCHECKED_LIGHT_PRESSED), master=self)
            self.im_unchecked_rest = ImageTk.PhotoImage(Image.open(IM_UNCHECKED_LIGHT_REST), master=self)

            self.im_tristate_focus = ImageTk.PhotoImage(Image.open(IM_TRISTATE_LIGHT_FOCUS), master=self)
            self.im_tristate_pressed = ImageTk.PhotoImage(Image.open(IM_TRISTATE_LIGHT_PRESSED), master=self)
            self.im_tristate_rest = ImageTk.PhotoImage(Image.open(IM_TRISTATE_LIGHT_REST), master=self)

        self.tag_configure("checked_focus", image=self.im_checked_focus)
        self.tag_configure("checked_pressed", image=self.im_checked_pressed)
        self.tag_configure("checked", image=self.im_checked_rest)

        self.tag_configure("unchecked_focus", image=self.im_unchecked_focus)
        self.tag_configure("unchecked_pressed", image=self.im_unchecked_pressed)
        self.tag_configure("unchecked", image=self.im_unchecked_rest)

        self.tag_configure("tristate_focus", image=self.im_tristate_focus)
        self.tag_configure("tristate_pressed", image=self.im_tristate_pressed)
        self.tag_configure("tristate", image=self.im_tristate_rest)
