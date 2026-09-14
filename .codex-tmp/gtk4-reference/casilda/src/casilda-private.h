/*
 * Casilda Private Functions
 *
 * Copyright (C) 2026  Juan Pablo Ugarte
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation;
 * version 2.1 of the License.
 *
 * library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * Authors:
 *   Val Packett <val@packett.cool>
 *
 * SPDX-License-Identifier: LGPL-2.1-only
 */

#pragma once

#include <gtk/gtk.h>
#include <wlr/backend.h>
#include <wlr/types/wlr_seat.h>

/* casilda-buffer.c */

G_GNUC_INTERNAL
void casilda_buffer_configure_shm (struct wl_display *wl_display);

G_GNUC_INTERNAL
void casilda_buffer_configure_dmabuf (struct wl_display *wl_display);

G_GNUC_INTERNAL
GdkTexture *casilda_buffer_texture_from_wlr (struct wlr_buffer *buffer,
                                             pixman_region32_t *damage,
                                             GdkTexture *prev);

/* casilda-data-source.c */

G_GNUC_INTERNAL
struct wlr_data_source *casilda_data_source_new (GObject *gdk_source);

typedef void (*CasildaDataSourceCallback)(GdkContentProvider *provider,
                                          gpointer            userdata);

G_GNUC_INTERNAL
void casilda_data_source_read_async (struct wlr_data_source *source,
                                     CasildaDataSourceCallback callback,
                                     gpointer                  userdata);

G_GNUC_INTERNAL
GdkDragAction casilda_data_source_action_from_wl (enum wl_data_device_manager_dnd_action actions);

G_GNUC_INTERNAL
enum wl_data_device_manager_dnd_action casilda_data_source_dnd_action_from_gdk (GdkDragAction actions);

/* casilda-content-provider.c */

G_GNUC_INTERNAL
GdkContentProvider *casilda_content_provider_new (struct wlr_data_source *source);
