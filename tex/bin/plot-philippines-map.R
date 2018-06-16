#! /usr/bin/env Rscript

library(maps)
library(mapdata)
library(ggplot2)

points = read.delim("localities.csv", sep = ",", header = TRUE)
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
               color = "black",
               size = 1.5,
               show.legend = FALSE) +
    geom_point(data = cyrt_points,
               aes(x = long2, y = lat2),
               color = "black",
               size = 1.5,
               show.legend = FALSE) +
    geom_segment(data = cyrt_points,
                 aes(x = long1, y = lat1,
                     xend = long2, yend=lat2),
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
               color = "black",
               size = 1.5,
               show.legend = FALSE) +
    geom_point(data = cyrt_points,
               aes(x = long2, y = lat2),
               color = "black",
               size = 1.5,
               show.legend = FALSE) +
    geom_segment(data = cyrt_points,
                 aes(x = long1, y = lat1,
                     xend = long2, yend=lat2),
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
               color = "black",
               size = 1.5,
               show.legend = FALSE) +
    geom_point(data = gekko_points,
               aes(x = long2, y = lat2),
               color = "black",
               size = 1.5,
               show.legend = FALSE) +
    geom_segment(data = gekko_points,
                 aes(x = long1, y = lat1,
                     xend = long2, yend=lat2),
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
               color = "black",
               size = 1.5,
               show.legend = FALSE) +
    geom_point(data = gekko_points,
               aes(x = long2, y = lat2),
               color = "black",
               size = 1.5,
               show.legend = FALSE) +
    geom_segment(data = gekko_points,
                 aes(x = long1, y = lat1,
                     xend = long2, yend=lat2),
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
