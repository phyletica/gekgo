#! /usr/bin/env Rscript

library(maps)
library(mapdata)
library(ggplot2)
library(viridis)

point_size = 3.7
legend_point_size = 4.0
legend_point_shape = 15
legend_title_font_size = 14.0
legend_label_font_size = 14.0
line_size = 1.9
pgreen = rgb(50, 162, 81, max = 255)
porange = rgb(255, 127, 15, max = 255)
pblue = rgb(60, 183, 204, max = 255)
pyellow = rgb(255, 217, 74, max = 255)
pteal = rgb(57, 115, 124, max = 255)
pauburn = rgb(184, 90, 13, max = 255)

# How I got these colors from matplotlib:
# import matplotlib
# v = matplotlib.cm.get_cmap("viridis")
# v(0.0, bytes = True)
viridis00 = rgb(68, 1, 84, max = 255)
# v(0.5, bytes = True)
viridis05 = rgb(32, 144, 140, max = 255)
# v(1.0, bytes = True)
viridis10 = rgb(253, 231, 36, max = 255)
viridis_colors = viridis(100)


points = read.delim("phycoeval-localities.tsv", sep = "\t", header = TRUE)

gekko_points = subset(points, genus == "Gekko")
cyrt_points = subset(points, genus == "Cyrtodactylus")

d = map_data("worldHires", c("Philippines", "Malaysia", "Indonesia"))
p = ggplot() +
    geom_polygon(data = d, aes(x = long, y = lat, group = group),
                 fill = "gray",
                 # color = "black",
                 ) +
    coord_fixed(xlim = c(116.8, 126.2),
                ylim = c(6.15, 20.2),
                ratio = 1.0) +
    theme_minimal(base_size = 14) +
    labs(x = "Longitude") +
    labs(y = "Latitude") +
    geom_point(data = cyrt_points,
               aes(x = long, y = lat),
               color = pauburn,
               size = point_size,
               show.legend = FALSE)

ggsave("../images/phycoeval-map-cyrt.pdf", width = 5.0, height = 7.0, units = "in")
ggsave("../images/phycoeval-map-cyrt.png", width = 5.0, height = 7.0, units = "in")
ggsave("../images/phycoeval-map-cyrt.svg", width = 5.0, height = 7.0, units = "in")

p = ggplot() +
    geom_polygon(data = d, aes(x = long, y = lat, group = group),
                 fill = "gray",
                 # color = "black",
                 ) +
    coord_fixed(xlim = c(116.8, 126.2),
                ylim = c(6.15, 20.2),
                ratio = 1.0) +
    theme_minimal(base_size = 14) +
    labs(x = "Longitude") +
    labs(y = "Latitude") +
    geom_point(data = gekko_points,
               aes(x = long, y = lat),
               color = pteal,
               size = point_size,
               show.legend = FALSE)

ggsave("../images/phycoeval-map-gekko.pdf", width = 5.0, height = 7.0, units = "in")
ggsave("../images/phycoeval-map-gekko.png", width = 5.0, height = 7.0, units = "in")
ggsave("../images/phycoeval-map-gekko.svg", width = 5.0, height = 7.0, units = "in")
