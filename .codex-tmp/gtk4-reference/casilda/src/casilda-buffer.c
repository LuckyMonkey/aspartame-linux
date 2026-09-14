/* casilda-buffersc: internal buffer management functions
 *
 * Copyright (C) 2026 Val Packett
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * SPDX-License-Identifier: LGPL-2.1-only
 */

#define _POSIX_C_SOURCE 200809L /* dirfd, readlinkat, fstatat */
#define WLR_USE_UNSTABLE 1
#define G_LOG_DOMAIN "Casilda"

#include <drm_fourcc.h>
#include <wlr/types/wlr_compositor.h>
#include <wlr/types/wlr_linux_dmabuf_v1.h>
#include <wlr/types/wlr_shm.h>
#include "casilda-private.h"
#include "casilda-config.h"

#define FORMAT_UNSUPPORTED ((GdkMemoryFormat)-1)

#ifdef ENABLE_DMABUF

#if G_BYTE_ORDER == G_LITTLE_ENDIAN
#  if (GTK_MAJOR_VERSION == 4) && (GTK_MINOR_VERSION >= 24)
#    define DRM_FORMATS_MAP_LE_GTK_4_24 \
    DRM_FORMAT(GDK_MEMORY_ARGB2101010_PREMULTIPLIED, DRM_FORMAT_ARGB2101010) \
    DRM_FORMAT(GDK_MEMORY_XRGB2101010, DRM_FORMAT_XRGB2101010) \
    DRM_FORMAT(GDK_MEMORY_ABGR2101010_PREMULTIPLIED, DRM_FORMAT_ABGR2101010) \
    DRM_FORMAT(GDK_MEMORY_XBGR2101010, DRM_FORMAT_XBGR2101010)
#  else
#    define DRM_FORMATS_MAP_LE_GTK_4_24
#  endif
#  define DRM_FORMATS_MAP_LE \
    DRM_FORMAT(GDK_MEMORY_R16G16B16A16_PREMULTIPLIED, DRM_FORMAT_ABGR16161616) \
    DRM_FORMAT(GDK_MEMORY_R16G16B16A16_FLOAT_PREMULTIPLIED, DRM_FORMAT_ABGR16161616F) \
    DRM_FORMAT(GDK_MEMORY_G10X6_B10X6R10X6_420, DRM_FORMAT_P010) \
    DRM_FORMAT(GDK_MEMORY_G12X4_B12X4R12X4_420, DRM_FORMAT_P012) \
    DRM_FORMAT(GDK_MEMORY_G16_B16R16_420, DRM_FORMAT_P016) \
    DRM_FORMAT(GDK_MEMORY_X6G10_X6B10_X6R10_420, DRM_FORMAT_S010) \
    DRM_FORMAT(GDK_MEMORY_X6G10_X6B10_X6R10_422, DRM_FORMAT_S210) \
    DRM_FORMAT(GDK_MEMORY_X6G10_X6B10_X6R10_444, DRM_FORMAT_S410) \
    DRM_FORMAT(GDK_MEMORY_X4G12_X4B12_X4R12_420, DRM_FORMAT_S012) \
    DRM_FORMAT(GDK_MEMORY_X4G12_X4B12_X4R12_422, DRM_FORMAT_S212) \
    DRM_FORMAT(GDK_MEMORY_X4G12_X4B12_X4R12_444, DRM_FORMAT_S412) \
    DRM_FORMAT(GDK_MEMORY_G16_B16_R16_420, DRM_FORMAT_S016) \
    DRM_FORMAT(GDK_MEMORY_G16_B16_R16_422, DRM_FORMAT_S216) \
    DRM_FORMAT(GDK_MEMORY_G16_B16_R16_444, DRM_FORMAT_S416) \
    DRM_FORMATS_MAP_LE_GTK_4_24
#else
#  define DRM_FORMATS_MAP_LE
#endif

#define DRM_FORMATS_MAP \
    DRM_FORMAT(GDK_MEMORY_B8G8R8A8_PREMULTIPLIED, DRM_FORMAT_ARGB8888) \
    DRM_FORMAT(GDK_MEMORY_A8R8G8B8_PREMULTIPLIED, DRM_FORMAT_BGRA8888) \
    DRM_FORMAT(GDK_MEMORY_B8G8R8X8, DRM_FORMAT_XRGB8888) \
    DRM_FORMAT(GDK_MEMORY_X8R8G8B8, DRM_FORMAT_BGRX8888) \
    DRM_FORMAT(GDK_MEMORY_B8G8R8, DRM_FORMAT_RGB888) \
    DRM_FORMAT(GDK_MEMORY_R8G8B8, DRM_FORMAT_BGR888) \
    DRM_FORMAT(GDK_MEMORY_G8, DRM_FORMAT_R8) \
    DRM_FORMAT(GDK_MEMORY_G16, DRM_FORMAT_R16) \
    DRM_FORMAT(GDK_MEMORY_G8_B8R8_420, DRM_FORMAT_NV12) \
    DRM_FORMAT(GDK_MEMORY_G8_R8B8_420, DRM_FORMAT_NV21) \
    DRM_FORMAT(GDK_MEMORY_G8_B8R8_422, DRM_FORMAT_NV16) \
    DRM_FORMAT(GDK_MEMORY_G8_R8B8_422, DRM_FORMAT_NV61) \
    DRM_FORMAT(GDK_MEMORY_G8_B8R8_444, DRM_FORMAT_NV24) \
    DRM_FORMAT(GDK_MEMORY_G8_R8B8_444, DRM_FORMAT_NV42) \
    DRM_FORMAT(GDK_MEMORY_G8_B8_R8_410, DRM_FORMAT_YUV410) \
    DRM_FORMAT(GDK_MEMORY_G8_R8_B8_410, DRM_FORMAT_YVU410) \
    DRM_FORMAT(GDK_MEMORY_G8_B8_R8_411, DRM_FORMAT_YUV411) \
    DRM_FORMAT(GDK_MEMORY_G8_R8_B8_411, DRM_FORMAT_YVU411) \
    DRM_FORMAT(GDK_MEMORY_G8_B8_R8_420, DRM_FORMAT_YUV420) \
    DRM_FORMAT(GDK_MEMORY_G8_R8_B8_420, DRM_FORMAT_YVU420) \
    DRM_FORMAT(GDK_MEMORY_G8_B8_R8_422, DRM_FORMAT_YUV422) \
    DRM_FORMAT(GDK_MEMORY_G8_R8_B8_422, DRM_FORMAT_YVU422) \
    DRM_FORMAT(GDK_MEMORY_G8_B8_R8_444, DRM_FORMAT_YUV444) \
    DRM_FORMAT(GDK_MEMORY_G8_R8_B8_444, DRM_FORMAT_YVU444) \
    DRM_FORMAT(GDK_MEMORY_G8B8G8R8_422, DRM_FORMAT_YUYV) \
    DRM_FORMAT(GDK_MEMORY_G8R8G8B8_422, DRM_FORMAT_YVYU) \
    DRM_FORMAT(GDK_MEMORY_B8G8R8G8_422, DRM_FORMAT_UYVY) \
    DRM_FORMAT(GDK_MEMORY_R8G8B8G8_422, DRM_FORMAT_VYUY) \
    DRM_FORMATS_MAP_LE
#else

#define DRM_FORMATS_MAP \
    DRM_FORMAT(GDK_MEMORY_B8G8R8A8_PREMULTIPLIED, DRM_FORMAT_ARGB8888) \
    DRM_FORMAT(GDK_MEMORY_A8R8G8B8_PREMULTIPLIED, DRM_FORMAT_BGRA8888) \
    DRM_FORMAT(GDK_MEMORY_B8G8R8X8, DRM_FORMAT_XRGB8888) \
    DRM_FORMAT(GDK_MEMORY_X8R8G8B8, DRM_FORMAT_BGRX8888) \
    DRM_FORMAT(GDK_MEMORY_B8G8R8, DRM_FORMAT_RGB888) \
    DRM_FORMAT(GDK_MEMORY_R8G8B8, DRM_FORMAT_BGR888)

#endif

static inline GdkMemoryFormat
_gdk_format_from_drm_format (const uint32_t fourcc)
{
  switch (fourcc)
    {
#define DRM_FORMAT(gdk, drm) \
    case drm: \
      return gdk;
DRM_FORMATS_MAP
#undef DRM_FORMAT
    default:
      return FORMAT_UNSUPPORTED;
    }
}

/* Literally the same type internally, but no public conversion API.. */
static inline cairo_region_t *
cairo_region_from_pixman (pixman_region32_t *pixman_region)
{
  cairo_region_t *region = cairo_region_create ();
  const pixman_box32_t *rects = NULL;
  int n_rects = 0;

  rects = pixman_region32_rectangles (pixman_region, &n_rects);
  for (int i = 0; i < n_rects; i++)
    {
      const pixman_box32_t *r = &rects[i];
      cairo_region_union_rectangle (region, &(cairo_rectangle_int_t){ r->x1, r->y1, r->x2 - r->x1, r->y2 - r->y1 });
    }

  return region;
}

static inline GdkTexture *
wlr_shm_buffer_as_gdk (struct wlr_buffer *buffer, struct wlr_shm_attributes *attrs, pixman_region32_t *damage, GdkTexture *prev)
{
  g_autoptr (GdkMemoryTextureBuilder) builder = gdk_memory_texture_builder_new ();
  g_autoptr (GBytes) bytes = NULL;
  GdkMemoryFormat format;
  uint32_t drm_format;
  size_t stride;
  void *data;

  if (!wlr_buffer_begin_data_ptr_access (buffer, WLR_BUFFER_DATA_PTR_ACCESS_READ,
                                         &data, &drm_format, &stride))
    {
      g_warning ("Failed to access shared memory buffer %p", buffer);
      return NULL;
    }

  format = _gdk_format_from_drm_format (drm_format);

  if (format == FORMAT_UNSUPPORTED)
    {
      g_warning_once ("Unsupported texture format %x", format);
      wlr_buffer_end_data_ptr_access (buffer);
      return NULL;
    }

  gdk_memory_texture_builder_set_format (builder, format);
  gdk_memory_texture_builder_set_width (builder, attrs->width);
  gdk_memory_texture_builder_set_height (builder, attrs->height);
  gdk_memory_texture_builder_set_stride (builder, stride);
  gdk_memory_texture_builder_set_update_texture (builder, prev);

  /* Copy to have ownership, buffer will be gone after exit from the commit listener */
  bytes = g_bytes_new (data, stride * attrs->height);
  gdk_memory_texture_builder_set_bytes (builder, bytes);

  if (damage && pixman_region32_not_empty (damage))
    {
      cairo_region_t *region = cairo_region_from_pixman (damage);
      gdk_memory_texture_builder_set_update_region (builder, region);
      cairo_region_destroy (region);
    }

  GdkTexture *result = gdk_memory_texture_builder_build (builder);
  wlr_buffer_end_data_ptr_access (buffer);
  return result;
}

void
casilda_buffer_configure_shm (struct wl_display *wl_display)
{
#define DRM_FORMAT(gdk, drm) drm,
  static const uint32_t shm_formats[] = { DRM_FORMATS_MAP };
#undef DRM_FORMAT

  wlr_shm_create (wl_display, 2, shm_formats, G_N_ELEMENTS (shm_formats));
}


#ifdef ENABLE_DMABUF

typedef struct {
  int n_planes;
  int fd[WLR_DMABUF_MAX_PLANES];
} PlaneFileDescriptors;

static void
free_owned_fds (gpointer data)
{
  PlaneFileDescriptors *owned_fds = data;

  for (int i = 0; i < owned_fds->n_planes; i++)
    close (owned_fds->fd[i]);

  g_free (owned_fds);
}

static inline GdkTexture *
wlr_dmabuf_buffer_as_gdk (struct wlr_dmabuf_attributes *attrs, pixman_region32_t *damage, GdkTexture *prev)
{
  g_autoptr (GdkDmabufTextureBuilder) builder = gdk_dmabuf_texture_builder_new ();
  g_autoptr (GError) error = NULL;
  PlaneFileDescriptors *owned_fds = g_new0 (PlaneFileDescriptors, 1);
  owned_fds->n_planes = attrs->n_planes;

  gdk_dmabuf_texture_builder_set_width (builder, attrs->width);
  gdk_dmabuf_texture_builder_set_height (builder, attrs->height);
  gdk_dmabuf_texture_builder_set_fourcc (builder, attrs->format);
  gdk_dmabuf_texture_builder_set_modifier (builder, attrs->modifier);
  gdk_dmabuf_texture_builder_set_n_planes (builder, attrs->n_planes);

  for (int i = 0; i < attrs->n_planes; i++)
    {
      gdk_dmabuf_texture_builder_set_fd (builder, i, owned_fds->fd[i] = dup(attrs->fd[i]));
      gdk_dmabuf_texture_builder_set_offset (builder, i, attrs->offset[i]);
      gdk_dmabuf_texture_builder_set_stride (builder, i, attrs->stride[i]);
    }

  gdk_dmabuf_texture_builder_set_update_texture (builder, prev);

  if (damage && pixman_region32_not_empty (damage))
    {
      cairo_region_t *region = cairo_region_from_pixman (damage);
      gdk_dmabuf_texture_builder_set_update_region (builder, region);
      cairo_region_destroy (region);
    }

  GdkTexture *result = gdk_dmabuf_texture_builder_build (builder, free_owned_fds, owned_fds, &error);
  if (error)
    {
      g_warning ("Failed to import dmabuf texture: %s", error->message);
      free_owned_fds (owned_fds);
    }
  return result;
}

static dev_t
find_used_drm_node ()
{
  dev_t result = 0;
  char target_name[PATH_MAX] = {0};
  struct dirent *dp;
  struct stat stat;

  DIR *dir = opendir ("/proc/self/fd");
  if (!dir)
    {
      g_warning ("Could not open /proc/self/fd");
      return result;
    }

  int dir_fd = dirfd (dir);
  while ((dp = readdir (dir)) != NULL) {
    if (strcmp (dp->d_name, ".") == 0 || strcmp (dp->d_name, "..") == 0)
      continue;
    ssize_t len = readlinkat (dir_fd, dp->d_name, target_name, PATH_MAX - 1);
    if (len < 0)
      continue;
    target_name[len] = '\0';
    if (strncmp (target_name, "/dev/dri/", sizeof ("/dev/dri")) != 0)
      continue;
    if (fstatat (dir_fd, dp->d_name, &stat, 0 /* do follow symlink */) == 0)
      {
        result = stat.st_rdev;
        goto dev_found;
      }
    else
      g_warning ("Could not stat fd %s (%s)\n", dp->d_name, target_name);
  }
  g_warning ("drm node used by GTK not found");

dev_found:
  closedir (dir);
  return result;
}

static dev_t
find_first_drm_node ()
{
  dev_t result = 0;
  struct dirent *dp;
  struct stat stat;

  DIR *dir = opendir ("/dev/dri");
  if (!dir)
    {
      g_warning ("Could not open /dev/dri");
      return result;
    }

  int dir_fd = dirfd (dir);
  while ((dp = readdir (dir)) != NULL) {
    if (strcmp (dp->d_name, ".") == 0 || strcmp (dp->d_name, "..") == 0)
      continue;
    if (fstatat (dir_fd, dp->d_name, &stat, 0) == 0)
      {
        result = stat.st_rdev;
        goto dev_found;
      }
    else
      g_warning ("Could not stat drm node %s\n", dp->d_name);
  }
  g_warning ("First drm node not found");

dev_found:
  closedir (dir);
  return result;
}

void
casilda_buffer_configure_dmabuf (struct wl_display *wl_display)
{
  GdkDmabufFormats *gdk_formats = gdk_display_get_dmabuf_formats (gdk_display_get_default ());
  struct wlr_linux_dmabuf_feedback_v1 feedback = {0};
  struct wlr_linux_dmabuf_feedback_v1_tranche *tranche =
    wlr_linux_dmabuf_feedback_add_tranche (&feedback);
  size_t n_formats = gdk_dmabuf_formats_get_n_formats (gdk_formats);
  uint32_t fourcc;
  uint64_t modifier;

  for (size_t i = 0; i < n_formats; i++)
    {
      // Unfortunately gdk_display_get_dmabuf_formats returns the list of formats supported
      // by the *actual host compositor* which is **not** the same thing as the list of
      // formats supported by Gdk for importing!
      // https://gitlab.gnome.org/GNOME/gtk/-/issues/8148
      gdk_dmabuf_formats_get_format (gdk_formats, i, &fourcc, &modifier);

#define DRM_FORMAT(gdk, drm) case drm:

      switch (fourcc)
        {
          DRM_FORMATS_MAP
            if (!wlr_drm_format_set_add (&tranche->formats, fourcc, modifier))
              g_warning ("Failed to add dmabuf format %x/%lx", fourcc, modifier);
          break;
          default:
            g_debug ("Skipping dmabuf format %x/%lx as unknown to Gdk", fourcc, modifier);
        }
    }
#undef DRM_FORMAT

  // Unfortunately GTK does not share which DRM node it is using..
  // https://gitlab.gnome.org/GNOME/gtk/-/issues/8149
#ifdef __linux__
  feedback.main_device = tranche->target_device = find_used_drm_node();
#endif
  if (!feedback.main_device)
    feedback.main_device = tranche->target_device = find_first_drm_node();

  if (feedback.main_device)
    {
      wlr_linux_dmabuf_v1_create (wl_display, 5, &feedback);
      wlr_linux_dmabuf_feedback_v1_finish (&feedback);
    }
}

#else

void
casilda_buffer_configure_dmabuf (G_GNUC_UNUSED struct wl_display *wl_display)
{
  g_warning ("DMABUF support is not enabled");
}

#endif

GdkTexture *
casilda_buffer_texture_from_wlr (struct wlr_buffer *buffer, pixman_region32_t *damage, GdkTexture *prev)
{
#ifdef ENABLE_DMABUF
  struct wlr_dmabuf_attributes dmabuf_attrs;

  if (wlr_buffer_get_dmabuf (buffer, &dmabuf_attrs))
    return wlr_dmabuf_buffer_as_gdk (&dmabuf_attrs, damage, prev);
#endif

  struct wlr_shm_attributes shm_attrs;

  if (wlr_buffer_get_shm (buffer, &shm_attrs))
    return wlr_shm_buffer_as_gdk (buffer, &shm_attrs, damage, prev);

  g_warning ("Unsupported buffer kind @ %p", buffer);
  return NULL;
}
