#! /usr/bin/env Rscript

library(maps)
library(mapdata)
library(ggplot2)

point_size = 2.7
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


# connected_color = pauburn
# maybe_connected_color = pgreen
# not_connected_color = pteal
connected_color = viridis00
maybe_connected_color = viridis05 
not_connected_color = viridis10

get_color = function(x) {
    if (x == "yes") {
        return(connected_color)
    }
    else if (x == "no") {
        return(not_connected_color)
    }
    else {
        return(maybe_connected_color)
    }
}

points = read.delim("localities.csv", sep = ",", header = TRUE)
points$color = mapply(get_color, points$connected)

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
               aes(x = long1, y = lat1),
               color = cyrt_points$color,
               size = point_size,
               show.legend = FALSE) +
    geom_point(data = cyrt_points,
               aes(x = long2, y = lat2),
               color = cyrt_points$color,
               size = point_size,
               show.legend = FALSE) +
    geom_segment(data = cyrt_points,
                 aes(x = long1, y = lat1,
                     xend = long2, yend=lat2),
                 color = cyrt_points$color,
                 size = line_size,
                 show.legend = FALSE) +
    geom_text(data = cyrt_points,
              aes(x = long1, y = lat1,
                  label = as.character(island1),
                  hjust = as.character(hjust1),
                  vjust = as.character(vjust1)),
              nudge_x = cyrt_points$nudge_x1,
              nudge_y = cyrt_points$nudge_y1,
              show.legend = FALSE) +
    geom_text(data = cyrt_points,
              aes(x = long2, y = lat2,
                  label = as.character(island2),
                  hjust = as.character(hjust2),
                  vjust = as.character(vjust2)),
              nudge_x = cyrt_points$nudge_x2,
              nudge_y = cyrt_points$nudge_y2,
              show.legend = FALSE)

ggsave("../images/map-cyrt.pdf", width = 5.0, height = 7.0, units = "in")
ggsave("../images/map-cyrt.png", width = 5.0, height = 7.0, units = "in")
ggsave("../images/map-cyrt.svg", width = 5.0, height = 7.0, units = "in")

p = ggplot() +
    geom_polygon(data = d, aes(x = long, y = lat, group = group),
                 fill = "gray",
                 # color = "black",
                 ) +
    coord_fixed(xlim = c(116.8, 126.2),
                ylim = c(6.15, 20.2),
                ratio = 1.0) +
    theme_minimal(base_size = 14) +
    labs(x = "") +
    labs(y = "") +
    geom_point(data = cyrt_points,
               aes(x = long1, y = lat1),
               color = cyrt_points$color,
               size = point_size,
               show.legend = FALSE) +
    geom_point(data = cyrt_points,
               aes(x = long2, y = lat2),
               color = cyrt_points$color,
               size = point_size,
               show.legend = FALSE) +
    geom_segment(data = cyrt_points,
                 aes(x = long1, y = lat1,
                     xend = long2, yend=lat2),
                 color = cyrt_points$color,
                 size = line_size,
                 show.legend = FALSE) +
    geom_text(data = cyrt_points,
              aes(x = long1, y = lat1,
                  label = as.character(island1),
                  hjust = as.character(hjust1),
                  vjust = as.character(vjust1)),
              nudge_x = cyrt_points$nudge_x1,
              nudge_y = cyrt_points$nudge_y1,
              show.legend = FALSE) +
    geom_text(data = cyrt_points,
              aes(x = long2, y = lat2,
                  label = as.character(island2),
                  hjust = as.character(hjust2),
                  vjust = as.character(vjust2)),
              nudge_x = cyrt_points$nudge_x2,
              nudge_y = cyrt_points$nudge_y2,
              show.legend = FALSE) +
    geom_polygon(aes(x = c(116.4, 119.3, 119.3, 116.4),
                     y = c(15.0, 15.0, 17.5, 17.5)),
                 fill = "gray94",
                 color = "gray60",
                 show.legend = FALSE) +
    geom_text(aes(x = 116.6, y = 17.15,
                  label = "Connected?",
                  size = legend_title_font_size,
                  hjust = "left",
                  vjust = "center"),
              fontface = "bold",
              show.legend = FALSE) +
    geom_point(aes(x = 116.8, y = 16.60),
               color = connected_color,
               size = legend_point_size,
               shape = legend_point_shape,
               show.legend = FALSE) +
    geom_text(aes(x = 116.8, y = 16.60,
                  label = "Yes",
                  size = legend_label_font_size,
                  hjust = "left",
                  vjust = "center"),
              show.legend = FALSE,
              nudge_x = 0.3) +
    geom_point(aes(x = 116.8, y = 16.05),
               color = maybe_connected_color,
               size = legend_point_size,
               shape = legend_point_shape,
               show.legend = FALSE) +
    geom_text(aes(x = 116.8, y = 16.05,
                  label = "Maybe",
                  size = legend_label_font_size,
                  hjust = "left",
                  vjust = "center"),
              show.legend = FALSE,
              nudge_x = 0.3) +
    geom_point(aes(x = 116.8, y = 15.5),
               color = not_connected_color,
               size = legend_point_size,
               shape = legend_point_shape,
               show.legend = FALSE) +
    geom_text(aes(x = 116.8, y = 15.5,
                  label = "No",
                  size = legend_label_font_size,
                  hjust = "left",
                  vjust = "center"),
              show.legend = FALSE,
              nudge_x = 0.3)

ggsave("../images/map-cyrt-no-labels.pdf", width = 5.0, height = 7.0, units = "in")

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
               aes(x = long1, y = lat1),
               color = gekko_points$color,
               size = point_size,
               show.legend = FALSE) +
    geom_point(data = gekko_points,
               aes(x = long2, y = lat2),
               color = gekko_points$color,
               size = point_size,
               show.legend = FALSE) +
    geom_segment(data = gekko_points,
                 aes(x = long1, y = lat1,
                     xend = long2, yend=lat2),
                 color = gekko_points$color,
                 size = line_size,
                 show.legend = FALSE) +
    geom_text(data = gekko_points,
              aes(x = long1, y = lat1,
                  label = as.character(island1),
                  hjust = as.character(hjust1),
                  vjust = as.character(vjust1)),
              nudge_x = gekko_points$nudge_x1,
              nudge_y = gekko_points$nudge_y1,
              show.legend = FALSE) +
    geom_text(data = gekko_points,
              aes(x = long2, y = lat2,
                  label = as.character(island2),
                  hjust = as.character(hjust2),
                  vjust = as.character(vjust2)),
              nudge_x = gekko_points$nudge_x2,
              nudge_y = gekko_points$nudge_y2,
              show.legend = FALSE)

ggsave("../images/map-gekko.pdf", width = 5.0, height = 7.0, units = "in")
ggsave("../images/map-gekko.png", width = 5.0, height = 7.0, units = "in")
ggsave("../images/map-gekko.svg", width = 5.0, height = 7.0, units = "in")

p = ggplot() +
    geom_polygon(data = d, aes(x = long, y = lat, group = group),
                 fill = "gray",
                 # color = "black",
                 ) +
    coord_fixed(xlim = c(116.8, 126.2),
                ylim = c(6.15, 20.2),
                ratio = 1.0) +
    theme_minimal(base_size = 14) +
    labs(x = "") +
    labs(y = "") +
    geom_point(data = gekko_points,
               aes(x = long1, y = lat1),
               color = gekko_points$color,
               size = point_size,
               show.legend = FALSE) +
    geom_point(data = gekko_points,
               aes(x = long2, y = lat2),
               color = gekko_points$color,
               size = point_size,
               show.legend = FALSE) +
    geom_segment(data = gekko_points,
                 aes(x = long1, y = lat1,
                     xend = long2, yend=lat2),
                 color = gekko_points$color,
                 size = line_size,
                 show.legend = FALSE) +
    geom_text(data = gekko_points,
              aes(x = long1, y = lat1,
                  label = as.character(island1),
                  hjust = as.character(hjust1),
                  vjust = as.character(vjust1)),
              nudge_x = gekko_points$nudge_x1,
              nudge_y = gekko_points$nudge_y1,
              show.legend = FALSE) +
    geom_text(data = gekko_points,
              aes(x = long2, y = lat2,
                  label = as.character(island2),
                  hjust = as.character(hjust2),
                  vjust = as.character(vjust2)),
              nudge_x = gekko_points$nudge_x2,
              nudge_y = gekko_points$nudge_y2,
              show.legend = FALSE)

ggsave("../images/map-gekko-no-labels.pdf", width = 5.0, height = 7.0, units = "in")
