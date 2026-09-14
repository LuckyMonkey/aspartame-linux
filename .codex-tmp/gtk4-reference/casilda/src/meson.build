api_version = '1.0'

casilda_sources = [
  'casilda-buffer.c',
  'casilda-compositor.c',
  'casilda-content-provider.c',
  'casilda-data-source.c',
  'casilda-wayland-source.c',
]

casilda_headers = [
  'casilda.h',
  'casilda-compositor.h',
]

version_conf = configuration_data()
version_conf.set('VERSION', meson.project_version())
version_conf.set('MAJOR_VERSION', version_split[0])
version_conf.set('MINOR_VERSION', version_split[1])
version_conf.set('MICRO_VERSION', version_split[2])

casilda_headers += configure_file(
  input: 'casilda-version.h.in',
  output: 'casilda-version.h',
  configuration: version_conf,
  install: true,
  install_dir: get_option('includedir') / 'casilda',
)

casilda_deps = [
  gtk4_dep,
  gio_unix_dep,
  libdrm_dep,
  wlroots_dep,
  xkbcommon,
  wayland_server_dep,
  pixman_dep
]

lib_c_args = []
if xkbcommon_x11_dep.found() and x11_xcb_dep.found()
  casilda_deps += [xkbcommon_x11_dep, x11_xcb_dep]
  lib_c_args += ['-DHAVE_X11_XCB=1']
endif

# Remove soversion once Meson is updated to support this automatically
# https://mesonbuild.com/Reference-manual_functions.html#shared_library_version
casilda_lib = shared_library('casilda-' + api_version,
  sources: [
    casilda_sources
  ],
  version: api_version,
  soversion: api_version.split('.')[0],
  dependencies: casilda_deps,
  c_args: lib_c_args,
  link_args : '-lm',
  install: true,
)

casilda_dep = declare_dependency(
  include_directories: include_directories('.'),
  link_with: casilda_lib,
  dependencies: gtk4_dep,
)

install_headers(casilda_headers, subdir: 'casilda')

pkg.generate(
  description: 'A simple Gtk wayland compositor widget',
  libraries: casilda_lib,
  name: 'casilda',
  filebase: 'casilda-' + api_version,
  version: meson.project_version(),
  subdirs: 'casilda',
  requires: [ gtk4_dep ],
  requires_private: [ wlroots_dep ],
  install_dir: get_option('libdir') / 'pkgconfig'
)

casilda_gir = gnome.generate_gir(casilda_lib,
  sources: [casilda_headers, casilda_sources],
  nsversion: api_version,
  namespace: 'Casilda',
  symbol_prefix: 'casilda',
  identifier_prefix: 'Casilda',
  includes: [ 'Gtk-4.0' ],
  install: true,
  extra_args: [ '--c-include=casilda.h' ]
)

if get_option('vapi')
    casilda_vapi = gnome.generate_vapi('casilda-' + api_version,
      sources: casilda_gir[0],
      install: true,
      packages: [ 'gtk4' ],
      install_dir: get_option('datadir') / 'vala' / 'vapi',
      metadata_dirs: [ meson.current_source_dir() ]
    )
endif
