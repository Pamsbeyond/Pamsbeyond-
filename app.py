import io
import json
import random
import pandas as pd
import plotly.express as px
import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer

import base64
import os
import re
from datetime import date, timedelta
from pathlib import Path

import streamlit.components.v1 as components

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="PamsBeyond - Visa & Travel Global Services",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to hide Streamlit header and padding for full-screen feel
st.markdown('<meta name="google-site-verification" content="J6rOwP_5k6lkMPyWC4DVqG2TztlklkLQ9Az8qZSSP-A" />', unsafe_allow_html=True)

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
        iframe {
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

# Single Page HTML/CSS/JS Web App Component

def _offline_plan(origin,destination,period,budget):
    return f"""Pams travel plan\n\nRoute: {origin} to {destination}\nTravel period: {period}\nTotal budget: ${budget:,.0f}\n\nSuggested allocation\n- Flights: about 35% (${budget*.35:,.0f})\n- Accommodation: about 35% (${budget*.35:,.0f})\n- Food and local transport: about 20% (${budget*.20:,.0f})\n- Experiences and contingency: about 10% (${budget*.10:,.0f})\n\nItinerary framework\n- Arrival day: settle in, local orientation, and a nearby evening walk.\n- Exploration days: one signature landmark, one local neighbourhood, and one flexible discovery activity each day.\n- Final day: reserve time for shopping, packing, and the return journey.\n\nThis is a planning estimate. Verify prices, availability, entry rules, and official visa information before booking."""


def _make_pdf(text):
    if not A4: return None
    b=io.BytesIO(); doc=SimpleDocTemplate(b,pagesize=A4,rightMargin=16*mm,leftMargin=16*mm,topMargin=16*mm,bottomMargin=16*mm); styles=getSampleStyleSheet(); story=[Paragraph("Pams Travel Plan",styles["Title"]),Spacer(1,8)]
    for line in text.split("\\n"):
        if not line.strip(): story.append(Spacer(1,5)); continue
        story += [Paragraph(line.replace("&","&amp;"),styles["Heading2"] if line.endswith(":") else styles["BodyText"]),Spacer(1,3)]
    doc.build(story); return b.getvalue()

html_code = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="google-site-verification" content="J6rOwP_5k6lkMPyWC4DVqG2TztlklkLQ9Az8qZSSP-A" />
    <title>PamsBeyond | Visa Help, Flights, Hotels & Local Travel Services</title>
    <meta name="description" content="Plan international travel with PamsBeyond: visa guidance, flight comparisons, accommodation ideas, airport transfers, local transport, destination guides, and practical travel tips.">
    <meta name="keywords" content="travel planning, visa help, flight search, airport transfer, hotel booking, destination guides, travel tips">
    <meta property="og:title" content="PamsBeyond | Make your next journey easier">
    <meta property="og:description" content="Travel support for visas, flights, stays, transfers, destination ideas, and practical trip planning.">
    <meta property="og:type" content="website">
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"TravelAgency","name":"PamsBeyond","description":"Travel support for visa guidance, flight discovery, accommodation ideas, local transport, and destination planning.","serviceType":["Travel planning","Visa guidance","Flight search","Airport transfers","Accommodation discovery"]}</script>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Leaflet OpenStreetMap CSS & JS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        brandRed: '#dc2626',
                        brandRedDark: '#991b1b',
                        brandNavy: '#dbeafe',
                        brandBlack: '#f8fafc',
                        brandGray: '#eef2ff',
                        brandCard: '#ffffff'
                    },
                    fontFamily: {
                        sans: ['Inter', 'system-ui', 'sans-serif'],
                    }
                }
            }
        }
    </script>
    <style>
        /* Custom scrollbars */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #f8fafc; }
        ::-webkit-scrollbar-thumb { background: #e60023; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #b3001b; }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.92);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(124, 58, 237, 0.20);
        }
        .glass-card-hover {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .glass-card-hover:hover {
            transform: translateY(-4px);
            border-color: rgba(124, 58, 237, 0.6);
            box-shadow: 0 10px 30px -10px rgba(124, 58, 237, 0.25);
        }
        
        /* Dynamic Background Canvas */
        #bgCanvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            pointer-events: none;
        }

        /* Animated pulse glow */
        @keyframes redGlow {
            0%, 100% { box-shadow: 0 0 15px rgba(230, 0, 35, 0.4); }
            50% { box-shadow: 0 0 30px rgba(230, 0, 35, 0.8); }
        }
        .glow-red {
            animation: redGlow 3s infinite;
        }

        /* Logo blend styling without white background */
        .logo-container img {
            display: block;
            width: 100%;
            height: 100%;
            object-fit: contain;
            mix-blend-mode: normal;
            filter: none;
        }
    </style>
</head>
<body class="bg-brandBlack text-slate-900 font-sans min-h-screen flex flex-col relative overflow-x-hidden">

    <!-- LIVE ANIMATED CANVAS BACKGROUND (Flying Planes) -->
    <canvas id="bgCanvas"></canvas>

    <!-- TOP HEADER / NAVIGATION -->
    <header class="sticky top-0 z-40 glass-card border-b border-brandRed/20 px-4 lg:px-8 py-3">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
            <!-- Brand Logo & Name -->
            <a href="#" onclick="switchTab('home')" class="flex items-center gap-3 group">
                <div class="relative w-20 h-14 flex items-center justify-center bg-brandRed rounded-xl overflow-hidden border-2 border-purple-200 shadow-lg logo-container">
                    <span class="text-3xl font-serif italic font-black text-white tracking-tight">Pams</span>
                    <i class="fa-solid fa-rocket absolute text-white text-xs -right-1 top-1 rotate-12"></i>
                    <i class="fa-solid fa-suitcase-rolling absolute text-purple-200 text-[11px] left-1 bottom-1 -rotate-12"></i>
                </div>
                <div>
                    <span class="text-2xl font-black tracking-tight text-slate-900 uppercase">Pams<span class="text-brandRed">Beyond</span></span>
                    <p class="text-[10px] text-slate-500 tracking-widest uppercase font-semibold">AI Travel Services</p>
                </div>
            </a>

            <!-- Navigation Links -->
            <nav class="hidden md:flex items-center gap-1 bg-white/80 p-1.5 rounded-full border border-gray-800">
                <button onclick="switchTab('visa')" class="nav-btn px-4 py-2 rounded-full text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-brandRed/20 transition flex items-center gap-2">
                    <i class="fa-solid fa-passport text-brandRed"></i> Visas
                </button>
                <button onclick="switchTab('flights')" class="nav-btn px-4 py-2 rounded-full text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-brandRed/20 transition flex items-center gap-2">
                    <i class="fa-solid fa-plane-departure text-brandRed"></i> Flights
                </button>
                <button onclick="switchTab('hotels')" class="nav-btn px-4 py-2 rounded-full text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-brandRed/20 transition flex items-center gap-2">
                    <i class="fa-solid fa-hotel text-brandRed"></i> Stays
                </button>
                <button onclick="switchTab('help')" class="nav-btn px-4 py-2 rounded-full text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-brandRed/20 transition flex items-center gap-2">
                    <i class="fa-solid fa-map-location-dot text-brandRed"></i> Local Assistance
                </button>
            </nav>

            <!-- Quick Live Chat Button -->
            <button onclick="toggleChatbot()" class="px-5 py-2.5 rounded-full bg-brandRed hover:bg-brandRedDark text-slate-900 font-bold text-xs tracking-wider transition shadow-lg shadow-brandRed/30 flex items-center gap-2">
                <i class="fa-solid fa-comments"></i> Live Chat
            </button>
        </div>
    </header>

    <!-- MAIN CONTENT CONTAINER -->
    <main class="relative z-10 flex-grow max-w-7xl w-full mx-auto px-4 py-8">

        <!-- ================================================================= -->
        <!-- VIEW 0: MAIN DASHBOARD -->
        <!-- ================================================================= -->
        <section id="view-home" class="space-y-10">
            <!-- Hero Banner -->
            <div class="text-center space-y-4 max-w-3xl mx-auto pt-6">
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brandRed/10 border border-brandRed/30 text-brandRed text-xs font-bold uppercase tracking-wider">
                    <i class="fa-solid fa-compass"></i> Worldwide Visa & Travel Assistance
                </div>
                <h1 class="text-3xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
                    Tell us where the next overseas plans
                </h1>
                <p class="text-slate-500 text-sm sm:text-base">
                    Select your travel service below. From instant global visa requirements to flights, accommodations, and local ground support.
                </p>
            </div>

            <!-- Dashboard Options -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">

                <!-- CARD 1 -->
                <div onclick="switchTab('visa')" class="glass-card glass-card-hover p-6 sm:p-8 rounded-2xl cursor-pointer group relative overflow-hidden flex flex-col justify-between min-h-[220px]">
                    <div class="absolute -right-8 -bottom-8 opacity-10 group-hover:opacity-25 transition text-brandRed">
                        <i class="fa-solid fa-passport text-9xl"></i>
                    </div>
                    <div>
                        <div class="w-12 h-12 rounded-xl bg-brandRed/20 border border-brandRed/40 flex items-center justify-center text-brandRed text-2xl mb-4 group-hover:bg-brandRed group-hover:text-slate-900 transition">
                            <i class="fa-solid fa-passport"></i>
                        </div>
                        <span class="text-xs font-bold text-brandRed uppercase tracking-widest">What we can do for you</span>
                        <h2 class="text-2xl font-bold text-slate-900 mt-1 group-hover:text-brandRed transition">Planning to travel to get yourself overseas?</h2>
                        <p class="text-slate-500 text-xs sm:text-sm mt-2">Instant search for worldwide visa requirements, documentation, exact official fees, and direct officer support.</p>
                    </div>
                    <div class="mt-6 flex items-center text-xs font-bold text-brandRed group-hover:translate-x-2 transition">
                        Explore Visa Requirements <i class="fa-solid fa-arrow-right ml-2"></i>
                    </div>
                </div>

                <!-- CARD 2 -->
                <div onclick="switchTab('flights')" class="glass-card glass-card-hover p-6 sm:p-8 rounded-2xl cursor-pointer group relative overflow-hidden flex flex-col justify-between min-h-[220px]">
                    <div class="absolute -right-8 -bottom-8 opacity-10 group-hover:opacity-25 transition text-brandRed">
                        <i class="fa-solid fa-plane text-9xl"></i>
                    </div>
                    <div>
                        <div class="w-12 h-12 rounded-xl bg-brandRed/20 border border-brandRed/40 flex items-center justify-center text-brandRed text-2xl mb-4 group-hover:bg-brandRed group-hover:text-slate-900 transition">
                            <i class="fa-solid fa-plane-departure"></i>
                        </div>
                        <span class="text-xs font-bold text-brandRed uppercase tracking-widest">What we can do for you</span>
                        <h2 class="text-2xl font-bold text-slate-900 mt-1 group-hover:text-brandRed transition">Need a flight booking?</h2>
                        <p class="text-slate-500 text-xs sm:text-sm mt-2">Scans global airlines & booking platforms by city to display live lowest rates and best connection routes.</p>
                    </div>
                    <div class="mt-6 flex items-center text-xs font-bold text-brandRed group-hover:translate-x-2 transition">
                        Find Best Flights <i class="fa-solid fa-arrow-right ml-2"></i>
                    </div>
                </div>

                <!-- CARD 3 -->
                <div onclick="switchTab('hotels')" class="glass-card glass-card-hover p-6 sm:p-8 rounded-2xl cursor-pointer group relative overflow-hidden flex flex-col justify-between min-h-[220px]">
                    <div class="absolute -right-8 -bottom-8 opacity-10 group-hover:opacity-25 transition text-brandRed">
                        <i class="fa-solid fa-hotel text-9xl"></i>
                    </div>
                    <div>
                        <div class="w-12 h-12 rounded-xl bg-brandRed/20 border border-brandRed/40 flex items-center justify-center text-brandRed text-2xl mb-4 group-hover:bg-brandRed group-hover:text-slate-900 transition">
                            <i class="fa-solid fa-hotel"></i>
                        </div>
                        <span class="text-xs font-bold text-brandRed uppercase tracking-widest">What we can do for you</span>
                        <h2 class="text-2xl font-bold text-slate-900 mt-1 group-hover:text-brandRed transition">Any accommodation?</h2>
                        <p class="text-slate-500 text-xs sm:text-sm mt-2">Discover high-rated properties globally with interactive price filters and luxury or budget recommendations.</p>
                    </div>
                    <div class="mt-6 flex items-center text-xs font-bold text-brandRed group-hover:translate-x-2 transition">
                        Search Accommodations <i class="fa-solid fa-arrow-right ml-2"></i>
                    </div>
                </div>

                <!-- CARD 4 -->
                <div onclick="switchTab('help')" class="glass-card glass-card-hover p-6 sm:p-8 rounded-2xl cursor-pointer group relative overflow-hidden flex flex-col justify-between min-h-[220px]">
                    <div class="absolute -right-8 -bottom-8 opacity-10 group-hover:opacity-25 transition text-brandRed">
                        <i class="fa-solid fa-taxi text-9xl"></i>
                    </div>
                    <div>
                        <div class="w-12 h-12 rounded-xl bg-brandRed/20 border border-brandRed/40 flex items-center justify-center text-brandRed text-2xl mb-4 group-hover:bg-brandRed group-hover:text-slate-900 transition">
                            <i class="fa-solid fa-map-location-dot"></i>
                        </div>
                        <span class="text-xs font-bold text-brandRed uppercase tracking-widest">What we can do for you</span>
                        <h2 class="text-2xl font-bold text-slate-900 mt-1 group-hover:text-brandRed transition">You are already there and need any help?</h2>
                        <p class="text-slate-500 text-xs sm:text-sm mt-2">Airport pickup, taxis, local transit, top nearby restaurants and hotels powered by live map discovery.</p>
                    </div>
                    <div class="mt-6 flex items-center text-xs font-bold text-brandRed group-hover:translate-x-2 transition">
                        Locate Nearby Services <i class="fa-solid fa-arrow-right ml-2"></i>
                    </div>
                </div>

            </div>
                <!-- PHOTO-LED AFFILIATE DISCOVERY BANNERS -->
                <section class="md:col-span-2 space-y-5">
                    <div class="flex items-end justify-between gap-4">
                        <div><span class="text-purple-600 text-xs font-bold uppercase tracking-widest">Plan the whole journey</span><h2 class="text-2xl sm:text-3xl font-black text-slate-900 mt-1">Good trips start with one smart choice</h2></div>
                        <span class="hidden sm:inline text-xs text-slate-500">Book with confidence</span>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        <a href="https://www.kiwi.com/en/" target="_blank" rel="noopener sponsored" class="group relative overflow-hidden rounded-2xl min-h-[210px] p-5 flex flex-col justify-end text-white shadow-lg bg-cover bg-center" style="background-image:linear-gradient(0deg,rgba(10,19,48,.9),rgba(10,19,48,.12)),url('https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1000&q=85')"><span class="relative text-[10px] font-extrabold uppercase tracking-widest text-cyan-200">Flights</span><h3 class="relative text-xl font-black mt-1">Find a clever route</h3><p class="relative text-xs text-blue-100 mt-1">Compare global connections and flexible combinations.</p><span class="relative inline-flex items-center gap-2 mt-4 text-xs font-bold">Search on Kiwi.com <i class="fa-solid fa-arrow-up-right-from-square"></i></span></a>
                        <a href="https://compensair.tpo.lu/zS2xTWji" target="_blank" rel="noopener sponsored" class="group relative overflow-hidden rounded-2xl min-h-[210px] p-5 flex flex-col justify-end text-white shadow-lg bg-cover bg-center" style="background-image:linear-gradient(0deg,rgba(44,17,74,.92),rgba(44,17,74,.08)),url('https://images.unsplash.com/photo-1517479149777-5f3b1511d5ad?auto=format&fit=crop&w=1000&q=85')"><span class="relative text-[10px] font-extrabold uppercase tracking-widest text-fuchsia-200">Flight support</span><h3 class="relative text-xl font-black mt-1">Turn delays into options</h3><p class="relative text-xs text-purple-100 mt-1">Get help when your journey does not go to plan.</p><span class="relative inline-flex items-center gap-2 mt-4 text-xs font-bold">Explore Compensair <i class="fa-solid fa-arrow-up-right-from-square"></i></span></a>
                        <a href="https://klook.tpo.lu/dNTBgDcE" target="_blank" rel="noopener sponsored" class="group relative overflow-hidden rounded-2xl min-h-[210px] p-5 flex flex-col justify-end text-white shadow-lg bg-cover bg-center" style="background-image:linear-gradient(0deg,rgba(106,39,4,.92),rgba(106,39,4,.08)),url('https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1000&q=85')"><span class="relative text-[10px] font-extrabold uppercase tracking-widest text-amber-100">Hotels · Tours · Services</span><h3 class="relative text-xl font-black mt-1">Make more of the destination</h3><p class="relative text-xs text-orange-100 mt-1">Stays, activities, transport, and memorable add-ons.</p><span class="relative inline-flex items-center gap-2 mt-4 text-xs font-bold">Explore Klook <i class="fa-solid fa-arrow-up-right-from-square"></i></span></a>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <a href="https://gettransfer.tpo.lu/VKCddkka" target="_blank" rel="noopener sponsored" class="group relative overflow-hidden rounded-2xl min-h-[150px] p-5 flex flex-col justify-end text-white shadow-lg bg-cover bg-center" style="background-image:linear-gradient(0deg,rgba(3,78,63,.94),rgba(3,78,63,.12)),url('https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=1000&q=85')"><span class="relative text-[10px] font-extrabold uppercase tracking-widest text-emerald-200">Airport transfers</span><h3 class="relative text-lg font-black mt-1">Land smoothly, move easily</h3><span class="relative inline-flex items-center gap-2 mt-3 text-xs font-bold">Book GetTransfer <i class="fa-solid fa-arrow-up-right-from-square"></i></span></a>
                        <a href="https://kiwitaxi.tpo.lu/FEwN4rkU" target="_blank" rel="noopener sponsored" class="group relative overflow-hidden rounded-2xl min-h-[150px] p-5 flex flex-col justify-end text-white shadow-lg bg-cover bg-center" style="background-image:linear-gradient(0deg,rgba(120,53,15,.94),rgba(120,53,15,.12)),url('https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&w=1000&q=85')"><span class="relative text-[10px] font-extrabold uppercase tracking-widest text-amber-200">Local rides</span><h3 class="relative text-lg font-black mt-1">Book a trusted taxi</h3><span class="relative inline-flex items-center gap-2 mt-3 text-xs font-bold">Find a Kiwitaxi ride <i class="fa-solid fa-arrow-up-right-from-square"></i></span></a>
                    </div>
                </section>

            <!-- ABOUT PAMS -->
            <section class="glass-card rounded-3xl p-6 sm:p-10 border border-purple-200 overflow-hidden">
                <div class="grid lg:grid-cols-[1.1fr_.9fr] gap-8 items-center">
                    <div>
                        <span class="text-brandRed text-xs font-bold uppercase tracking-widest">About Pams</span>
                        <h2 class="text-3xl sm:text-4xl font-black text-slate-900 mt-2">Travel support that feels human, wherever you start.</h2>
                        <p class="text-slate-600 mt-4 leading-relaxed">Pams is an AI travel services helper built with the experience of expert travel agents working across the Middle East, Austria, and the United States. It gives travellers a faster way to understand their options and plan with confidence.</p>
                        <div class="grid sm:grid-cols-2 gap-4 mt-6">
                            <div class="rounded-2xl bg-blue-50 border border-blue-200 p-4"><b class="text-slate-900">Is Pams human?</b><p class="text-slate-600 text-sm mt-1">Pams is an AI assistant supported by travel agents. Ask to talk to an agent and connect with a person in seconds, free of charge.</p></div>
                            <div class="rounded-2xl bg-purple-50 border border-purple-200 p-4"><b class="text-slate-900">Is it free?</b><p class="text-slate-600 text-sm mt-1">Pams is free to use. Fees apply only when you request an external service handled by an expert agent, such as application support or an embassy appointment.</p></div>
                        </div>
                        <p class="text-xs text-slate-500 mt-4">We do not archive personal information for these planning tools. External services are handled under the legal terms described in our policies.</p>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <img class="h-44 w-full object-cover rounded-2xl border-4 border-white shadow-xl rotate-[-2deg]" src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=700&q=80" alt="Airplane travelling above the clouds">
                        <img class="h-44 w-full object-cover rounded-2xl border-4 border-white shadow-xl rotate-[2deg] mt-7" src="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=700&q=80" alt="Beautiful travel destination">
                        <img class="h-36 w-full object-cover rounded-2xl border-4 border-white shadow-xl col-span-2" src="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=900&q=80" alt="Travel planning at a desk">
                    </div>
                </div>
            </section>

            <!-- DESTINATION GUIDES, TIPS, AND FAQ CONTENT HUB -->
            <section class="space-y-6">
                <div class="text-center max-w-3xl mx-auto"><span class="text-cyan-700 text-xs font-extrabold uppercase tracking-[0.2em]">Travel inspiration</span><h2 class="text-3xl sm:text-4xl font-black text-slate-900 mt-2">Ideas for the journey ahead</h2><p class="text-slate-600 mt-3">Short destination guides, practical tips, and answers to common travel questions — all in one place.</p></div>
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <article class="glass-card rounded-2xl overflow-hidden bg-white border border-blue-100"><img class="h-40 w-full object-cover" loading="lazy" src="https://images.unsplash.com/photo-1568322445389-f64ac2515020?auto=format&fit=crop&w=900&q=85" alt="Pyramids and desert landscape in Egypt"><div class="p-5"><span class="text-[10px] font-extrabold uppercase tracking-widest text-brandRed">Cairo & Luxor</span><h3 class="text-lg font-black text-slate-900 mt-1">Ancient sights, modern city energy</h3><p class="text-sm text-slate-600 mt-2">Pair Cairo’s museums and historic districts with Luxor’s temples and Nile-side mornings.</p><p class="text-xs text-slate-500 mt-3"><b>Tip:</b> Start major outdoor visits early and keep flexible time for traffic.</p></div></article>
                    <article class="glass-card rounded-2xl overflow-hidden bg-white border border-blue-100"><img class="h-40 w-full object-cover" loading="lazy" src="https://images.unsplash.com/photo-1518684079-3c830dcef090?auto=format&fit=crop&w=900&q=85" alt="Dubai skyline at sunset"><div class="p-5"><span class="text-[10px] font-extrabold uppercase tracking-widest text-brandRed">Dubai</span><h3 class="text-lg font-black text-slate-900 mt-1">Skyline, souks, and desert horizons</h3><p class="text-sm text-slate-600 mt-2">Build a balanced day with neighbourhood exploring, indoor attractions, and a sunset desert experience.</p><p class="text-xs text-slate-500 mt-3"><b>Tip:</b> Group activities by area to reduce cross-city travel time.</p></div></article>
                    <article class="glass-card rounded-2xl overflow-hidden bg-white border border-blue-100"><img class="h-40 w-full object-cover" loading="lazy" src="https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?auto=format&fit=crop&w=900&q=85" alt="Paris street and Eiffel Tower view"><div class="p-5"><span class="text-[10px] font-extrabold uppercase tracking-widest text-brandRed">Paris</span><h3 class="text-lg font-black text-slate-900 mt-1">Walkable culture with room to wander</h3><p class="text-sm text-slate-600 mt-2">Mix one headline landmark with a local market, a quiet garden, and an unplanned café stop.</p><p class="text-xs text-slate-500 mt-3"><b>Tip:</b> Reserve timed-entry attractions and leave space between bookings.</p></div></article>
                    <article class="glass-card rounded-2xl overflow-hidden bg-white border border-blue-100"><img class="h-40 w-full object-cover" loading="lazy" src="https://images.unsplash.com/photo-1513407030348-c983a97b98d8?auto=format&fit=crop&w=900&q=85" alt="Tokyo city lights and street scene"><div class="p-5"><span class="text-[10px] font-extrabold uppercase tracking-widest text-brandRed">Tokyo</span><h3 class="text-lg font-black text-slate-900 mt-1">Neighbourhoods that reward curiosity</h3><p class="text-sm text-slate-600 mt-2">Plan around districts so the day moves naturally from gardens and markets to food and evening lights.</p><p class="text-xs text-slate-500 mt-3"><b>Tip:</b> Save offline directions and check the last return connection.</p></div></article>
                </div>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
                    <div class="glass-card rounded-2xl p-6 sm:p-8 border border-cyan-100 bg-gradient-to-br from-cyan-50 to-white"><span class="text-cyan-700 text-xs font-extrabold uppercase tracking-widest">Practical travel tips</span><h3 class="text-2xl font-black text-slate-900 mt-2">A smoother trip starts before departure</h3><ul class="mt-4 space-y-3 text-sm text-slate-700"><li><i class="fa-solid fa-check text-cyan-700 mr-2"></i>Keep passport, insurance, bookings, and emergency contacts in one offline folder.</li><li><i class="fa-solid fa-check text-cyan-700 mr-2"></i>Compare the total journey, not only the headline fare: baggage, transfers, and timing matter.</li><li><i class="fa-solid fa-check text-cyan-700 mr-2"></i>Use a daily spending limit and leave a buffer for unexpected transport.</li><li><i class="fa-solid fa-check text-cyan-700 mr-2"></i>Check official embassy and airline information before relying on any third-party guide.</li></ul></div>
                    <div class="glass-card rounded-2xl p-6 sm:p-8 border border-purple-100 bg-white"><span class="text-purple-700 text-xs font-extrabold uppercase tracking-widest">Frequently asked questions</span><h3 class="text-2xl font-black text-slate-900 mt-2">Quick answers before you go</h3><div class="mt-4 space-y-3"><details class="border-b border-slate-200 pb-3"><summary class="cursor-pointer font-bold text-slate-900">Can PamsBeyond book my visa or flight directly?</summary><p class="text-sm text-slate-600 mt-2">PamsBeyond helps you compare options, understand requirements, and find useful travel services. Always review final terms with the provider.</p></details><details class="border-b border-slate-200 pb-3"><summary class="cursor-pointer font-bold text-slate-900">How early should I prepare for an international trip?</summary><p class="text-sm text-slate-600 mt-2">Start with passport validity, entry requirements, and transport availability. Timing varies by destination, season, and document requirements.</p></details><details><summary class="cursor-pointer font-bold text-slate-900">Are prices and availability guaranteed?</summary><p class="text-sm text-slate-600 mt-2">No. Prices, schedules, availability, and entry rules can change. Confirm current details with the official provider before paying or travelling.</p></details></div></div>
                </div>
            </section>

        </section>


        <!-- ================================================================= -->

        <!-- ================================================================= -->
        <!-- VIEW 1: VISA REQUIREMENTS -->
        <!-- ================================================================= -->
        <section id="view-visa" class="space-y-8 hidden">
            <div class="flex items-center justify-between border-b border-gray-800 pb-4">
                <div>
                    <span class="text-brandRed text-xs font-bold tracking-widest uppercase">What we can do for you</span>
                    <h1 class="text-3xl font-extrabold text-slate-900">Global Visa & Requirements Search</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1">
                    <i class="fa-solid fa-arrow-left"></i> Back to Main
                </button>
            </div>

            <div class="glass-card p-6 sm:p-8 rounded-2xl space-y-6">
                <form id="visaForm" onsubmit="event.preventDefault(); runVisaSearch();" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-flag text-brandRed"></i> 1. Origin Country</label>
                        <select id="visaOrigin" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="">Select Origin...</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-location-dot text-brandRed"></i> 2. Destination</label>
                        <select id="visaDest" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="">Select Destination...</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-id-card text-brandRed"></i> 3. Passport Type</label>
                        <select id="passportType" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="Ordinary Passport">Ordinary (Standard Tourist)</option>
                            <option value="Diplomatic Passport">Diplomatic Passport</option>
                            <option value="Official / Service Passport">Official / Service</option>
                            <option value="Refugee Travel Document">Refugee / Travel Document</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-briefcase text-brandRed"></i> 4. Visa Type</label>
                        <select id="visaType" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="Tourist Visa">Tourist Visa</option>
                        </select>
                    </div>

                    <div class="md:col-span-2 lg:col-span-4 mt-2">
                        <button type="submit" class="w-full py-4 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 font-bold text-sm tracking-wide transition shadow-lg shadow-brandRed/30 flex items-center justify-center gap-2">
                            <i class="fa-solid fa-magnifying-glass"></i> Search Requirements & Official Fees
                        </button>
                    </div>
                </form>
            </div>

            <!-- Visa Results -->
            <div id="visaResults" class="hidden space-y-6">
                <div class="glass-card p-6 sm:p-8 rounded-2xl border-l-4 border-l-brandRed space-y-6">
                    <div class="flex flex-wrap items-center justify-between gap-4 border-b border-gray-800 pb-4">
                        <div>
                            <span class="text-xs text-brandRed font-bold uppercase tracking-wider">Search Result</span>
                            <h2 id="resultTitle" class="text-2xl font-bold text-slate-900">Egypt ➔ Canada (Visitor Visa)</h2>
                        </div>
                        <div class="text-right">
                            <span class="text-xs text-slate-500 block">Official Govt Fee</span>
                            <span id="resultFee" class="text-2xl font-black text-brandRed">$100 USD + $85 Biometrics</span>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h3 class="text-sm font-bold text-slate-900 uppercase mb-3 flex items-center gap-2">
                                <i class="fa-solid fa-file-shield text-brandRed"></i> Required Documents Checklist
                            </h3>
                            <ul id="docList" class="space-y-2 text-xs sm:text-sm text-slate-600"></ul>
                        </div>
                        <div>
                            <h3 class="text-sm font-bold text-slate-900 uppercase mb-3 flex items-center gap-2">
                                <i class="fa-solid fa-gavel text-brandRed"></i> Key Terms & Entry Conditions
                            </h3>
                            <ul id="termsList" class="space-y-2 text-xs sm:text-sm text-slate-600"></ul>
                        </div>
                    </div>

                    <!-- HANDLING FOR YOU BOX -->
                    <div class="mt-6 p-6 rounded-xl bg-gradient-to-r from-brandNavy to-brandGray border border-brandRed/40 flex flex-col sm:flex-row items-center justify-between gap-4 glow-red">
                        <div>
                            <span class="bg-brandRed text-slate-900 text-[10px] font-extrabold px-2 py-0.5 rounded uppercase">Want to talk live to the agent</span>
                            <h3 class="text-lg font-bold text-slate-900 mt-1">Talk live with an experienced agent</h3>
                            <p id="offerText" class="text-xs text-slate-600 mt-1">Ask your questions directly and receive guidance from our officer team.</p>
                        </div>
                        <button onclick="triggerHandledAssistance()" class="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 font-extrabold text-xs whitespace-nowrap transition shadow-lg">
                            Talk to the agent live <i class="fa-solid fa-headset ml-1"></i>
                        </button>
                    </div>
                </div>
            </div>
        </section>


        <!-- ================================================================= -->
        <!-- VIEW 2: FLIGHT BOOKING SEARCH (CITY BASED) -->
        <!-- ================================================================= -->
        <section id="view-flights" class="space-y-8 hidden">
            <div class="flex items-center justify-between border-b border-gray-800 pb-4">
                <div>
                    <span class="text-brandRed text-xs font-bold tracking-widest uppercase">What we can do for you</span>
                    <h1 class="text-3xl font-extrabold text-slate-900">Need a suitable flight?</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1">
                    <i class="fa-solid fa-arrow-left"></i> Back to Main
                </button>
            </div>

            <div class="glass-card p-6 sm:p-8 rounded-2xl space-y-6">
                <div class="flex items-center gap-4 border-b border-gray-800 pb-4">
                    <label class="inline-flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="tripType" value="oneway" class="accent-brandRed" onchange="toggleReturnDate(false)">
                        <span class="text-sm font-semibold text-gray-200">One Way</span>
                    </label>
                    <label class="inline-flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="tripType" value="return" checked class="accent-brandRed" onchange="toggleReturnDate(true)">
                        <span class="text-sm font-semibold text-gray-200">Return Trip</span>
                    </label>
                </div>

                <!-- Flight Search Form with Cities -->
                <form id="flightForm" onsubmit="event.preventDefault(); runFlightSearch();" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-plane-departure text-brandRed"></i> Departure City</label>
                        <select id="flightOriginCity" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="">Select Departure City...</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-plane-arrival text-brandRed"></i> Destination City</label>
                        <select id="flightDestCity" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="">Select Arrival City...</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-calendar text-brandRed"></i> Departure Date</label>
                        <input type="date" id="flightDepDate" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                    </div>
                    <div id="returnDateContainer">
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-calendar-check text-brandRed"></i> Return Date</label>
                        <input type="date" id="flightRetDate" class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                    </div>

                    <div class="md:col-span-2 lg:col-span-4 mt-2">
                        <button type="submit" class="w-full py-4 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 font-bold text-sm tracking-wide transition shadow-lg shadow-brandRed/30 flex items-center justify-center gap-2">
                            <i class="fa-solid fa-magnifying-glass"></i> Scan Airlines & Compare Fares
                        </button>
                    </div>
                </form>
            </div>

            <!-- Flight Results -->
            <div id="flightResults" class="hidden space-y-4">
                <h3 class="text-xl font-bold text-slate-900 flex items-center gap-2">
                    <i class="fa-solid fa-plane text-brandRed"></i> Available Connection Deals
                </h3>
                <div id="flightList" class="space-y-4"></div>
                <div id="flightAffiliateLinks" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3"></div>
            </div>
        </section>


        <!-- ================================================================= -->
        <!-- VIEW 3: ACCOMMODATION -->
        <!-- ================================================================= -->
        <section id="view-hotels" class="space-y-8 hidden">
            <div class="flex items-center justify-between border-b border-gray-800 pb-4">
                <div>
                    <span class="text-brandRed text-xs font-bold tracking-widest uppercase">What we can do for you</span>
                    <h1 class="text-3xl font-extrabold text-slate-900">Find High-Rated Accommodations</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1">
                    <i class="fa-solid fa-arrow-left"></i> Back to Main
                </button>
            </div>

            <div class="glass-card p-6 sm:p-8 rounded-2xl space-y-6">
                <form id="hotelForm" onsubmit="event.preventDefault(); runHotelSearch();" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-city text-brandRed"></i> Destination City</label>
                        <select id="hotelLocation" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="">Choose Destination City...</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-calendar-day text-brandRed"></i> Check-in</label>
                        <input type="date" id="hotelCheckIn" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-calendar-day text-brandRed"></i> Check-out</label>
                        <input type="date" id="hotelCheckOut" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-users text-brandRed"></i> Guests & Rooms</label>
                        <select id="hotelGuests" class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="1 Guest, 1 Room">1 Guest, 1 Room</option>
                            <option value="2 Guests, 1 Room" selected>2 Guests, 1 Room</option>
                            <option value="4 Guests, 2 Rooms">4 Guests, 2 Rooms</option>
                        </select>
                    </div>

                    <div class="md:col-span-2 lg:col-span-4">
                        <button type="submit" class="w-full py-4 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 font-bold text-sm tracking-wide transition shadow-lg shadow-brandRed/30 flex items-center justify-center gap-2">
                            <i class="fa-solid fa-hotel"></i> Search Available Stays
                        </button>
                    </div>
                </form>
            </div>

            <!-- Hotel Output -->
            <div id="hotelResults" class="hidden space-y-6">
                <div class="glass-card p-4 rounded-xl flex flex-wrap items-center justify-between gap-4">
                    <div class="flex items-center gap-3">
                        <i class="fa-solid fa-sliders text-brandRed text-lg"></i>
                        <span class="text-sm font-bold text-slate-900">Price Filter:</span>
                        <input type="range" id="priceRange" min="50" max="1000" step="50" value="1000" oninput="filterHotels()" class="accent-brandRed cursor-pointer">
                        <span id="priceRangeValue" class="text-sm font-black text-brandRed">Up to $1000/night</span>
                    </div>
                    <div class="text-xs text-slate-500">
                        <span id="hotelCount">0</span> top-rated properties available
                    </div>
                </div>

                <div id="hotelList" class="grid grid-cols-1 md:grid-cols-3 gap-6"></div>
                <div id="hotelAffiliateLinks" class="mt-2"></div>
            </div>
        </section>


        <!-- ================================================================= -->
        <!-- VIEW 4: ON-GROUND HELP -->
        <!-- ================================================================= -->
        <section id="view-help" class="space-y-8 hidden">
            <div class="flex items-center justify-between border-b border-gray-800 pb-4">
                <div>
                    <span class="text-brandRed text-xs font-bold tracking-widest uppercase">What we can do for you</span>
                    <h1 class="text-3xl font-extrabold text-slate-900">Already There & Need Help?</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1">
                    <i class="fa-solid fa-arrow-left"></i> Back to Main
                </button>
            </div>

            <div class="glass-card p-6 rounded-2xl space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-location-crosshairs text-brandRed"></i> Current Location / City</label>
                        <input type="text" id="groundLocation" placeholder="e.g. Cairo, Paris, Toronto, Dubai" value="Cairo" class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-concierge-bell text-brandRed"></i> Required Assistance</label>
                        <select id="groundService" class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="Airport Pickup / Taxi">Airport Pickup & Taxi Booking</option>
                            <option value="Domestic Transportation">Domestic Transportation & Rentals</option>
                            <option value="Nearby Restaurants">Nearby Top Rated Restaurants</option>
                            <option value="Nearby Hotels">Emergency Nearby Hotels</option>
                        </select>
                    </div>
                    <div class="flex items-end">
                        <button onclick="runGroundSearch()" class="w-full py-3.5 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 font-bold text-sm tracking-wide transition shadow-lg shadow-brandRed/30 flex items-center justify-center gap-2">
                            <i class="fa-solid fa-map-pin"></i> Locate Nearby Services
                        </button>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 gap-6">
                <div class="glass-card rounded-2xl overflow-hidden p-2 min-h-[400px] flex flex-col">
                    <div id="map" class="w-full h-full min-h-[400px] rounded-xl z-10"></div>
                </div>
                <div id="groundAffiliateLinks" class="grid grid-cols-1 sm:grid-cols-3 gap-3"></div>
            </div>
        </section>

    </main>


    <!-- ================================================================= -->
    <!-- FLOATING LIVE CHATBOT WIDGET -->
    <!-- ================================================================= -->
    <div class="fixed bottom-6 right-6 z-50">
        <!-- Floating Toggle Button -->
        <button onclick="toggleChatbot()" class="w-14 h-14 rounded-full bg-brandRed hover:bg-brandRedDark text-slate-900 flex items-center justify-center shadow-2xl glow-red transition transform hover:scale-105">
            <i class="fa-solid fa-comments text-2xl"></i>
        </button>

        <!-- Chat Window -->
        <div id="chatBox" class="hidden absolute bottom-16 right-0 w-[340px] sm:w-[380px] h-[480px] glass-card rounded-2xl shadow-2xl flex flex-col overflow-hidden border-2 border-brandRed/50">
            <!-- Header -->
            <div class="bg-brandNavy p-4 border-b border-brandRed/30 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
                    <div>
                        <h4 class="text-sm font-bold text-slate-900">PamsBeyond Live Chat</h4>
                        <span class="text-[10px] text-slate-500">Human Officers Online</span>
                    </div>
                </div>
                <button onclick="toggleChatbot()" class="text-slate-500 hover:text-slate-900">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            </div>

            <!-- Messages Area -->
            <div id="chatMessages" class="flex-grow p-4 overflow-y-auto space-y-3 text-xs">
            </div>

            <!-- Pre-scripted Quick Options -->
            <div class="px-3 py-2 bg-white/80 border-t border-gray-800 flex gap-1.5 overflow-x-auto text-[10px]">
                <button onclick="switchTab('visa'); toggleChatbot();" class="px-2.5 py-1 rounded-full bg-brandRed/20 text-brandRed font-semibold whitespace-nowrap hover:bg-brandRed hover:text-slate-900 transition">Visa Help</button>
                <button onclick="switchTab('flights'); toggleChatbot();" class="px-2.5 py-1 rounded-full bg-brandRed/20 text-brandRed font-semibold whitespace-nowrap hover:bg-brandRed hover:text-slate-900 transition">Flight Deals</button>
                <button onclick="sendQuickMsg('Talk to Officer')" class="px-2.5 py-1 rounded-full bg-brandRed/20 text-brandRed font-semibold whitespace-nowrap hover:bg-brandRed hover:text-slate-900 transition">Speak to Officer</button>
            </div>

            <!-- Input Bar -->
            <form onsubmit="handleUserChat(event)" class="p-3 bg-brandBlack border-t border-gray-800 flex items-center gap-2">
                <input type="text" id="chatInput" placeholder="Type your inquiry..." class="flex-grow bg-brandGray border border-gray-700 rounded-xl px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-brandRed">
                <button type="submit" class="p-2 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 text-xs">
                    <i class="fa-solid fa-paper-plane"></i>
                </button>
            </form>
        </div>
    </div>


    <!-- ================================================================= -->
    <!-- MODAL: REQUEST ASSISTANCE / OFFICER FORM -->
    <!-- ================================================================= -->
    <div id="assistanceModal" class="fixed inset-0 z-50 bg-white/80 backdrop-blur-md hidden flex items-center justify-center p-4">
        <div class="glass-card max-w-lg w-full rounded-2xl p-6 sm:p-8 space-y-6 relative border-2 border-brandRed/50">
            <button onclick="closeAssistanceModal()" class="absolute top-4 right-4 text-slate-500 hover:text-slate-900">
                <i class="fa-solid fa-xmark text-xl"></i>
            </button>

            <div>
                <span class="text-brandRed text-xs font-bold uppercase tracking-widest">PamsBeyond Officers</span>
                <h2 class="text-2xl font-bold text-slate-900 mt-1">Feel free to talk to our experienced human officers</h2>
                <p class="text-xs text-slate-500 mt-1">Fill out your details to connect directly with an operational officer.</p>
            </div>

            <form id="assistanceForm" onsubmit="handleAssistanceSubmit(event)" class="space-y-4">
                <div>
                    <label class="block text-xs font-bold text-slate-600 uppercase mb-1">Full Name</label>
                    <input type="text" id="clientName" required placeholder="e.g. John Doe" class="w-full bg-white border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-600 uppercase mb-1">Email Address</label>
                    <input type="email" id="clientEmail" required placeholder="john@example.com" class="w-full bg-white border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-1">Visa Assistance</label>
                        <input type="text" id="modalVisaType" readonly class="w-full bg-brandGray border border-gray-800 rounded-xl px-3 py-2 text-xs text-slate-600">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-1">Other Services</label>
                        <select id="modalDest" class="w-full bg-brandGray border border-gray-800 rounded-xl px-3 py-2 text-xs text-slate-600">
                            <option value="Flights">Flights</option>
                            <option value="Hotels">Hotels</option>
                        </select>
                    </div>
                </div>

                <div id="freeConsultationNotice" class="p-3 bg-brandRed/10 border border-brandRed/30 rounded-xl text-xs text-brandRed font-semibold flex items-center gap-2">
                    <i class="fa-solid fa-circle-check"></i>
                    <span>Free consultation — no processing fees.</span>
                </div>

                <button type="submit" class="w-full py-3.5 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 font-bold text-sm tracking-wide transition shadow-lg shadow-brandRed/30 flex items-center justify-center gap-2">
                    <i class="fa-solid fa-paper-plane"></i> Connect With Officer Desk
                </button>
            </form>

            <div id="modalSuccess" class="hidden p-4 rounded-xl bg-green-900/40 border border-green-500 text-green-200 text-center text-xs space-y-2">
                <i class="fa-solid fa-circle-check text-2xl text-green-400"></i>
                <p class="font-bold">Request Sent Successfully!</p>
                <p>The officer will be with you shortly.</p>
            </div>
        </div>
    </div>


        <!-- PRIVACY POLICY PAGE -->
        <section id="view-privacy" class="space-y-8 hidden">
            <div class="flex items-center justify-between border-b border-gray-800 pb-4">
                <div>
                    <span class="text-brandRed text-xs font-bold tracking-widest uppercase">Trust & transparency</span>
                    <h1 class="text-3xl font-extrabold text-slate-900">Privacy Policy: Data Security & Document Handling</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1"><i class="fa-solid fa-arrow-left"></i> Back to Main</button>
            </div>
            <div class="glass-card p-6 sm:p-8 rounded-2xl space-y-8 text-sm text-slate-600 leading-relaxed">
                <p><strong class="text-slate-900">PamsBeyond</strong> is committed to protecting your personal data and ensuring transparency regarding how your information is handled.</p>
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">1. Handling of Identity Documents</h2><ul class="list-disc pl-5 space-y-2"><li><strong class="text-slate-900">Secure transmission:</strong> Documents provided for external services handled by our agents are transmitted using appropriate security measures to help protect them during processing.</li><li><strong class="text-slate-900">Limited scope:</strong> Documents are requested only when an external service is handled directly by one of our agents. We use them only for that requested service and do not archive them as part of the free planning tools.</li></ul></div>
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">2. Use of Email and Contact Information</h2><ul class="list-disc pl-5 space-y-2"><li><strong class="text-slate-900">Strictly for updates:</strong> Your email is collected for important updates, status notifications, and essential information about your request or booking.</li><li><strong class="text-slate-900">No spam or third-party sharing:</strong> We do not send spam or sell, rent, or share personal contact details with third parties for marketing or advertising.</li></ul></div>
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">3. Privacy Reminders</h2><ul class="list-disc pl-5 space-y-2"><li>Secure-transmission notices apply only to documents submitted for external services handled directly by our agents.</li><li>Email and checkout notices explain that contact information is used for request updates only.</li><li>When an external service is complete, we aim to remove service documents in line with the applicable policy and legal requirements.</li></ul></div>
            </div>
        </section>

        <!-- TERMS OF SERVICE PAGE -->
        <section id="view-terms" class="space-y-8 hidden">
            <div class="flex items-center justify-between border-b border-gray-800 pb-4">
                <div>
                    <span class="text-brandRed text-xs font-bold tracking-widest uppercase">Legal information</span>
                    <h1 class="text-3xl font-extrabold text-slate-900">PamsBeyond — Terms of Use</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1"><i class="fa-solid fa-arrow-left"></i> Back to Main</button>
            </div>
            <div class="glass-card p-6 sm:p-8 rounded-2xl space-y-8 text-sm text-slate-600 leading-relaxed">
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">1. Nature of Services and Disclaimer</h2><ul class="list-disc pl-5 space-y-2"><li><strong class="text-slate-900">Independent service provider:</strong> PamsBeyond provides AI-powered tools and human-assisted guidance for travel planning and visa application preparation.</li><li><strong class="text-slate-900">Not a government agency:</strong> PamsBeyond is not a government agency, embassy, or official consulate and cannot grant visas. Visa decisions rest solely with the relevant authorities and approval is not guaranteed.</li></ul></div>
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">2. Bookings and Third-Party Suppliers</h2><ul class="list-disc pl-5 space-y-2"><li>PamsBeyond compares flight and hotel prices and may link to third-party suppliers. We do not directly hold travel reservations.</li><li>Bookings are subject to supplier pricing, cancellation policies, and terms. PamsBeyond is not liable for supplier failures, delays, cancellations, or booking errors.</li></ul></div>
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">3. User Responsibilities</h2><ul class="list-disc pl-5 space-y-2"><li>Users must provide accurate, truthful, and current information.</li><li>Users are responsible for passport validity, vaccinations, transit visas, and other travel prerequisites.</li><li>Users must carefully review completed applications. If an error is identified on our part, PamsBeyond will work to correct it.</li></ul></div>
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">4. Fees, Payments, and Refund Policy</h2><ul class="list-disc pl-5 space-y-2"><li>PamsBeyond service fees cover preparation and filling services. Government fees, embassy charges, and third-party travel costs are separate.</li><li>Service fees are generally non-refundable. Visa rejection does not automatically qualify for a refund.</li><li>Fees for external agent services, government charges, and third-party travel costs are separate and are disclosed before the service begins.</li></ul></div>
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">5. Limitation of Liability</h2><p>PamsBeyond is not liable for financial losses, missed flights, denied boarding, or entry refusals caused by visa processing delays, embassy decisions, or inaccurate user-provided information. Liability is limited to the scope of application preparation and facilitation services.</p></div>
            </div>
        </section>

    <!-- FOOTER -->
    <footer class="relative z-10 glass-card border-t border-brandRed/20 mt-12 py-6 px-4 text-center text-xs text-slate-500">
        <p class="max-w-3xl mx-auto mb-4 text-slate-600">Dear friend, this app contains affiliate links. We may earn a commission if you book through them at no extra cost to you.</p>
        <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
            <div class="flex items-center gap-2">
                <span class="font-black text-slate-900 uppercase tracking-wider">pams<span class="text-brandRed">beyond</span></span>
                <span>&copy; <span id="year"></span>. All rights reserved.</span>
            </div>
            <div class="flex items-center gap-4 text-slate-500">
                <a href="#" onclick="switchTab('privacy'); return false;" class="hover:text-brandRed">Privacy Policy</a>
                <a href="#" onclick="switchTab('terms'); return false;" class="hover:text-brandRed">Terms of Service</a>
                <a href="#" onclick="openAssistanceModal('General Consultation', 'Flights'); return false;" class="hover:text-brandRed">Officer Desk</a>
            </div>
        </div>
    </footer>


    <!-- ================================================================= -->
    <!-- JAVASCRIPT LOGIC & ANIMATIONS -->
    <!-- ================================================================= -->
    <script>
        document.getElementById('year').textContent = new Date().getFullYear();

        // WORLD COUNTRIES
        const globalCountries = [
            "Afghanistan", "Albania", "Algeria", "Argentina", "Australia", "Austria", "Bahrain", 
            "Bangladesh", "Belgium", "Brazil", "Canada", "China", "Colombia", "Czech Republic", 
            "Denmark", "Egypt", "Finland", "France", "Germany", "Greece", "Hong Kong", "Hungary", 
            "India", "Indonesia", "Iran", "Iraq", "Ireland", "Italy", "Japan", "Jordan", 
            "Kuwait", "Lebanon", "Malaysia", "Mexico", "Morocco", "Netherlands", "New Zealand", 
            "Nigeria", "Norway", "Oman", "Pakistan", "Philippines", "Poland", "Portugal", 
            "Qatar", "Romania", "Saudi Arabia", "Singapore", "South Africa", "Spain", "Sweden", 
            "Switzerland", "Thailand", "Turkey", "UAE", "UK", "USA", "Vietnam"
        ];

        // GLOBAL CITIES (For Flight Search Option)
        const globalCities = [
            "Cairo (CAI) - Egypt", "Toronto (YYZ) - Canada", "Dubai (DXB) - UAE", 
            "London (LHR) - UK", "New York (JFK) - USA", "Paris (CDG) - France", 
            "Istanbul (IST) - Turkey", "Riyadh (RUH) - Saudi Arabia", "Sydney (SYD) - Australia", 
            "Tokyo (HND) - Japan", "Rome (FCO) - Italy", "Frankfurt (FRA) - Germany", 
            "Doha (DOH) - Qatar", "Bangkok (BKK) - Thailand", "Kuala Lumpur (KUL) - Malaysia"
        ];

        window.addEventListener('DOMContentLoaded', () => {
            // Populate Countries
            ['visaOrigin', 'visaDest', 'plannerOrigin', 'plannerDestination'].forEach(id => {
                const el = document.getElementById(id);
                if (!el) return;
                globalCountries.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c; opt.textContent = c;
                    el.appendChild(opt);
                });
            });

            // Populate Cities
            ['flightOriginCity', 'flightDestCity', 'hotelLocation'].forEach(id => {
                const el = document.getElementById(id);
                if (!el) return;
                globalCities.forEach(city => {
                    const opt = document.createElement('option');
                    opt.value = city; opt.textContent = city;
                    el.appendChild(opt);
                });
            });

            const today = new Date().toISOString().split('T')[0];
            const future = new Date(Date.now() + 86400000 * 7).toISOString().split('T')[0];
            ['flightDepDate', 'hotelCheckIn'].forEach(id => { if (document.getElementById(id)) document.getElementById(id).value = today; });
            ['flightRetDate', 'hotelCheckOut'].forEach(id => { if (document.getElementById(id)) document.getElementById(id).value = future; });

            initMap();
            initCanvas();
        });

        function switchTab(tabId) {
            ['home', 'planner', 'visa', 'flights', 'hotels', 'help', 'privacy', 'terms'].forEach(id => {
                const view = document.getElementById('view-' + id);
                if (view) view.classList.add('hidden');
            });
            const activeView = document.getElementById('view-' + tabId);
            if (!activeView) return;
            activeView.classList.remove('hidden');

            if(tabId === 'help' && leafletMap) {
                setTimeout(() => leafletMap.invalidateSize(), 300);
            }
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        const DESTINATIONS = [{"key":"hurghada","title":"Hurghada, Egypt","tag":"Red Sea diving and boat cruises","summary":"Red Sea diving and boat cruises","image":"https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=85","days":["Arrive in Hurghada, Egypt, settle in, and take an easy orientation walk.","Explore the signature sights and local neighbourhoods of Hurghada, Egypt.","Enjoy the main nature, beach, mountain, or cultural activity.","Take a guided day experience with time for a relaxed local meal.","Use a flexible day for markets, museums, viewpoints, or a nearby town.","Choose a second highlight, scenic excursion, or slower wellness day.","Enjoy a final breakfast and walk, then prepare for departure."]},{"key":"canary","title":"Canary Islands","tag":"Volcanic hiking, beaches, and mild island weather","summary":"Volcanic hiking, beaches, and mild island weather","image":"https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=85","days":["Arrive in Canary Islands, settle in, and take an easy orientation walk.","Explore the signature sights and local neighbourhoods of Canary Islands.","Enjoy the main nature, beach, mountain, or cultural activity.","Take a guided day experience with time for a relaxed local meal.","Use a flexible day for markets, museums, viewpoints, or a nearby town.","Choose a second highlight, scenic excursion, or slower wellness day.","Enjoy a final breakfast and walk, then prepare for departure."]},{"key":"bangkok-krabi","title":"Bangkok & Krabi, Thailand","tag":"Street food, temples, and Andaman island-hopping","summary":"Street food, temples, and Andaman island-hopping","image":"https://images.unsplash.com/photo-1508009603885-50cf7c579365?auto=format&fit=crop&w=1200&q=85","days":["Arrive in Bangkok & Krabi, Thailand, settle in, and take an easy orientation walk.","Explore the signature sights and local neighbourhoods of Bangkok & Krabi, Thailand.","Enjoy the main nature, beach, mountain, or cultural activity.","Take a guided day experience with time for a relaxed local meal.","Use a flexible day for markets, museums, viewpoints, or a nearby town.","Choose a second highlight, scenic excursion, or slower wellness day.","Enjoy a final breakfast and walk, then prepare for departure."]},{"key":"fulidhoo","title":"Fulidhoo, Maldives","tag":"Local-island beaches, reefs, and turquoise water","summary":"Local-island beaches, reefs, and turquoise water","image":"https://images.unsplash.com/photo-1514282401047-d79a71a590e8?auto=format&fit=crop&w=1200&q=85","days":["Arrive in Fulidhoo, Maldives, settle in, and take an easy orientation walk.","Explore the signature sights and local neighbourhoods of Fulidhoo, Maldives.","Enjoy the main nature, beach, mountain, or cultural activity.","Take a guided day experience with time for a relaxed local meal.","Use a flexible day for markets, museums, viewpoints, or a nearby town.","Choose a second highlight, scenic excursion, or slower wellness day.","Enjoy a final breakfast and walk, then prepare for departure."]},{"key":"sal","title":"Sal, Cape Verde","tag":"Atlantic beaches, salt flats, and ocean views","summary":"Atlantic beaches, salt flats, and ocean views","image":"https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=85","days":["Arrive in Sal, Cape Verde, settle in, and take an easy orientation walk.","Explore the signature sights and local neighbourhoods of Sal, Cape Verde.","Enjoy the main nature, beach, mountain, or cultural activity.","Take a guided day experience with time for a relaxed local meal.","Use a flexible day for markets, museums, viewpoints, or a nearby town.","Choose a second highlight, scenic excursion, or slower wellness day.","Enjoy a final breakfast and walk, then prepare for departure."]},{"key":"costa-rica","title":"Costa Rica Pacific Coast","tag":"Rainforest wildlife, volcanoes, and dry-season beaches","summary":"Rainforest wildlife, volcanoes, and dry-season beaches","image":"https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?auto=format&fit=crop&w=1200&q=85","days":["Arrive in Costa Rica Pacific Coast, settle in, and take an easy orientation walk.","Explore the signature sights and local neighbourhoods of Costa Rica Pacific Coast.","Enjoy the main nature, beach, mountain, or cultural activity.","Take a guided day experience with time for a relaxed local meal.","Use a flexible day for markets, museums, viewpoints, or a nearby town.","Choose a second highlight, scenic excursion, or slower wellness day.","Enjoy a final breakfast and walk, then prepare for departure."]},{"key":"zermatt-lucerne","title":"Swiss Alps: Zermatt & Lucerne","tag":"Snowy peaks, lifts, lakeside towns, and alpine views","summary":"Snowy peaks, lifts, lakeside towns, and alpine views","image":"https://images.unsplash.com/photo-1531366936337-7c912a4589a7?auto=format&fit=crop&w=1200&q=85","days":["Arrive in Swiss Alps: Zermatt & Lucerne, settle in, and take an easy orientation walk.","Explore the signature sights and local neighbourhoods of Swiss Alps: Zermatt & Lucerne.","Enjoy the main nature, beach, mountain, or cultural activity.","Take a guided day experience with time for a relaxed local meal.","Use a flexible day for markets, museums, viewpoints, or a nearby town.","Choose a second highlight, scenic excursion, or slower wellness day.","Enjoy a final breakfast and walk, then prepare for departure."]},{"key":"lapland","title":"Finnish Lapland","tag":"Aurora outings, huskies, reindeer, and snow","summary":"Aurora outings, huskies, reindeer, and snow","image":"https://images.unsplash.com/photo-1483347756197-71ef80e95f73?auto=format&fit=crop&w=1200&q=85","days":["Arrive in Finnish Lapland, settle in, and take an easy orientation walk.","Explore the signature sights and local neighbourhoods of Finnish Lapland.","Enjoy the main nature, beach, mountain, or cultural activity.","Take a guided day experience with time for a relaxed local meal.","Use a flexible day for markets, museums, viewpoints, or a nearby town.","Choose a second highlight, scenic excursion, or slower wellness day.","Enjoy a final breakfast and walk, then prepare for departure."]},{"key":"hokkaido","title":"Hokkaido, Japan","tag":"Powder skiing, markets, and onsen culture","summary":"Powder skiing, markets, and onsen culture","image":"https://images.unsplash.com/photo-1545569341-9eb8b30979d9?auto=format&fit=crop&w=1200&q=85","days":["Arrive in Hokkaido, Japan, settle in, and take an easy orientation walk.","Explore the signature sights and local neighbourhoods of Hokkaido, Japan.","Enjoy the main nature, beach, mountain, or cultural activity.","Take a guided day experience with time for a relaxed local meal.","Use a flexible day for markets, museums, viewpoints, or a nearby town.","Choose a second highlight, scenic excursion, or slower wellness day.","Enjoy a final breakfast and walk, then prepare for departure."]},{"key":"quebec","title":"Qu\u00e9bec City, Canada","tag":"Historic streets, snow activities, and winter food","summary":"Historic streets, snow activities, and winter food","image":"https://images.unsplash.com/photo-1519178614-68673b201f36?auto=format&fit=crop&w=1200&q=85","days":["Arrive in Qu\u00e9bec City, Canada, settle in, and take an easy orientation walk.","Explore the signature sights and local neighbourhoods of Qu\u00e9bec City, Canada.","Enjoy the main nature, beach, mountain, or cultural activity.","Take a guided day experience with time for a relaxed local meal.","Use a flexible day for markets, museums, viewpoints, or a nearby town.","Choose a second highlight, scenic excursion, or slower wellness day.","Enjoy a final breakfast and walk, then prepare for departure."]},{"key":"salzburg-innsbruck","title":"Austrian Alps: Salzburg & Innsbruck","tag":"Old towns, skiing, music, and snowy viewpoints","summary":"Old towns, skiing, music, and snowy viewpoints","image":"https://images.unsplash.com/photo-1516550893923-42d28e5677af?auto=format&fit=crop&w=1200&q=85","days":["Arrive in Austrian Alps: Salzburg & Innsbruck, settle in, and take an easy orientation walk.","Explore the signature sights and local neighbourhoods of Austrian Alps: Salzburg & Innsbruck.","Enjoy the main nature, beach, mountain, or cultural activity.","Take a guided day experience with time for a relaxed local meal.","Use a flexible day for markets, museums, viewpoints, or a nearby town.","Choose a second highlight, scenic excursion, or slower wellness day.","Enjoy a final breakfast and walk, then prepare for departure."]},{"key":"luxor-cairo","title":"Luxor & Cairo, Egypt","tag":"Pyramids, museums, temples, and Nile days","summary":"Pyramids, museums, temples, and Nile days","image":"https://images.unsplash.com/photo-1568322445389-f64ac2515020?auto=format&fit=crop&w=1200&q=85","days":["Arrive in Luxor & Cairo, Egypt, settle in, and take an easy orientation walk.","Explore the signature sights and local neighbourhoods of Luxor & Cairo, Egypt.","Enjoy the main nature, beach, mountain, or cultural activity.","Take a guided day experience with time for a relaxed local meal.","Use a flexible day for markets, museums, viewpoints, or a nearby town.","Choose a second highlight, scenic excursion, or slower wellness day.","Enjoy a final breakfast and walk, then prepare for departure."]},{"key":"new-york","title":"New York City, USA","tag":"Museums, skating, neighbourhood food, and skyline views","summary":"Museums, skating, neighbourhood food, and skyline views","image":"https://images.unsplash.com/photo-1496588152823-86ff7695e68f?auto=format&fit=crop&w=1200&q=85","days":["Arrive in New York City, USA, settle in, and take an easy orientation walk.","Explore the signature sights and local neighbourhoods of New York City, USA.","Enjoy the main nature, beach, mountain, or cultural activity.","Take a guided day experience with time for a relaxed local meal.","Use a flexible day for markets, museums, viewpoints, or a nearby town.","Choose a second highlight, scenic excursion, or slower wellness day.","Enjoy a final breakfast and walk, then prepare for departure."]},{"key":"da-nang","title":"Da Nang, Vietnam","tag":"Beach time, Hoi An, Marble Mountains, and local food","summary":"Beach time, Hoi An, Marble Mountains, and local food","image":"https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=1200&q=85","days":["Arrive in Da Nang, Vietnam, settle in, and take an easy orientation walk.","Explore the signature sights and local neighbourhoods of Da Nang, Vietnam.","Enjoy the main nature, beach, mountain, or cultural activity.","Take a guided day experience with time for a relaxed local meal.","Use a flexible day for markets, museums, viewpoints, or a nearby town.","Choose a second highlight, scenic excursion, or slower wellness day.","Enjoy a final breakfast and walk, then prepare for departure."]},{"key":"venice","title":"Venice, Italy","tag":"Quiet canals, art, architecture, and lagoon islands","summary":"Quiet canals, art, architecture, and lagoon islands","image":"https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?auto=format&fit=crop&w=1200&q=85","days":["Arrive in Venice, Italy, settle in, and take an easy orientation walk.","Explore the signature sights and local neighbourhoods of Venice, Italy.","Enjoy the main nature, beach, mountain, or cultural activity.","Take a guided day experience with time for a relaxed local meal.","Use a flexible day for markets, museums, viewpoints, or a nearby town.","Choose a second highlight, scenic excursion, or slower wellness day.","Enjoy a final breakfast and walk, then prepare for departure."]}];
        function escapeHtml(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));}
        function renderDestinationCards(){const g=document.getElementById('destinationGrid');if(!g)return;g.innerHTML=DESTINATIONS.map(d=>`<button type="button" onclick="showDestinationPlan('${d.key}')" class="text-left glass-card glass-card-hover rounded-2xl overflow-hidden border border-purple-200 bg-white group"><img src="${d.image}" alt="${escapeHtml(d.title)}" class="w-full h-44 object-cover group-hover:scale-105 transition duration-500" loading="lazy"><div class="p-5"><span class="text-[10px] font-bold uppercase tracking-widest text-purple-600">${escapeHtml(d.tag)}</span><h3 class="text-lg font-black text-slate-900 mt-1">${escapeHtml(d.title)}</h3><p class="text-sm text-slate-600 mt-2">${escapeHtml(d.summary)}</p><span class="inline-flex items-center mt-4 text-xs font-bold text-purple-600">Open 7-day itinerary <i class="fa-solid fa-arrow-right ml-2"></i></span></div></button>`).join('');}
        function showDestinationPlan(key){const d=DESTINATIONS.find(x=>x.key===key),r=document.getElementById('destinationPlan');if(!d||!r)return;const f=`https://www.google.com/travel/flights?q=Flights%20to%20${encodeURIComponent(d.title)}`,h=`https://www.booking.com/searchresults.html?ss=${encodeURIComponent(d.title)}`;r.innerHTML=`<div class="flex flex-col md:flex-row gap-5"><img src="${d.image}" alt="${escapeHtml(d.title)}" class="w-full md:w-72 h-48 object-cover rounded-2xl"><div><span class="text-purple-600 text-xs font-bold uppercase tracking-widest">${escapeHtml(d.tag)}</span><h2 class="text-3xl font-black text-slate-900 mt-1">${escapeHtml(d.title)}</h2><p class="text-slate-600 mt-2">${escapeHtml(d.summary)}</p><div class="flex gap-3 mt-4"><a class="text-xs font-bold text-brandRed" target="_blank" rel="noopener" href="${f}">Compare flights →</a><a class="text-xs font-bold text-brandRed" target="_blank" rel="noopener" href="${h}">Find stays →</a></div></div></div><h3 class="text-xl font-black text-slate-900">Your seven-day starting itinerary</h3><ol class="space-y-3">${d.days.map((day,i)=>`<li class="flex gap-3"><span class="shrink-0 w-8 h-8 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center text-xs font-black">${i+1}</span><p class="text-sm text-slate-700 pt-1">${escapeHtml(day)}</p></li>`).join('')}</ol><p class="text-xs text-slate-500 border-t border-slate-200 pt-4">Starting point only: verify weather, opening hours, prices, entry rules, and availability before booking.</p>`;r.classList.remove('hidden');r.scrollIntoView({behavior:'smooth',block:'start'});}
        renderDestinationCards();
        function generateTravelPlan(){
            const origin=document.getElementById('plannerOrigin').value;
            const destination=document.getElementById('plannerDestination').value;
            const period=document.getElementById('plannerPeriod').value.trim();
            const budget=Number(document.getElementById('plannerBudget').value);
            const results=document.getElementById('plannerResults');
            if(!origin||!destination||!period||!budget)return;
            const flightLink=`https://www.google.com/travel/flights?q=Flights%20from%20${encodeURIComponent(origin)}%20to%20${encodeURIComponent(destination)}`;
            const hotelLink=`https://www.booking.com/searchresults.html?ss=${encodeURIComponent(destination)}`;
            const placesLink=`https://www.google.com/maps/search/hidden+gems+in+${encodeURIComponent(destination)}`;
            const budgetNote=budget<800?'Focus on flexible dates, public transport, and locally owned stays.':budget<1800?'Balance comfortable stays with one or two priority experiences.':'Allow room for upgraded connections, central stays, and guided experiences.';
            results.innerHTML=`<h2 class="text-2xl font-black text-slate-900">${escapeHtml(origin)} to ${escapeHtml(destination)}</h2><p class="text-slate-600 text-sm">${escapeHtml(period)} · Budget: $${budget.toLocaleString()}</p><div class="grid md:grid-cols-2 gap-3 mt-4"><div class="rounded-2xl bg-blue-50 p-4"><b>Flights</b><p class="text-sm mt-1">Compare flexible connections.</p><a class="text-brandRed text-sm font-bold" target="_blank" rel="noopener" href="${flightLink}">Compare flights →</a></div><div class="rounded-2xl bg-purple-50 p-4"><b>Hotels</b><p class="text-sm mt-1">Filter stays by budget and dates.</p><a class="text-brandRed text-sm font-bold" target="_blank" rel="noopener" href="${hotelLink}">Find stays →</a></div><div class="rounded-2xl bg-red-50 p-4"><b>Places to explore</b><p class="text-sm mt-1">Find local highlights and hidden places.</p><a class="text-brandRed text-sm font-bold" target="_blank" rel="noopener" href="${placesLink}">Explore places →</a></div><div class="rounded-2xl bg-slate-50 p-4"><b>Budget guidance</b><p class="text-sm mt-1">${budgetNote}</p></div></div><p class="text-xs text-slate-500 mt-4">For AI-assisted itineraries, use the secure Streamlit planner panel at the top of the app.</p>`;
            results.classList.remove('hidden');
            results.scrollIntoView({behavior:'smooth'});
        }
        // VISA SEARCH LOGIC
        function runVisaSearch() {
            const origin = document.getElementById('visaOrigin').value;
            const dest = document.getElementById('visaDest').value;
            const passType = document.getElementById('passportType').value;
            const vType = document.getElementById('visaType').value;

            if(!origin || !dest) return;

            // Send the client's visa search details to PamsBeyond through FormSubmit.
            fetch('https://formsubmit.co/ajax/pamsbeyond@gmail.com', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    client_nationality: origin,
                    destination: dest,
                    visa_type: vType,
                    passport_type: passType,
                    _subject: `PamsBeyond Visa Search: ${origin} to ${dest}`,
                    _captcha: 'true',
                    _template: 'table'
                })
            }).catch(error => {
                console.error('Visa request notification failed:', error);
            });

            const resultsDiv = document.getElementById('visaResults');
            resultsDiv.classList.remove('hidden');

            document.getElementById('resultTitle').textContent = `${origin} ➔ ${dest} (${vType})`;
            
            let baseFee = 85;
            if (['USA', 'Canada', 'UK', 'Australia'].includes(dest)) baseFee = 150;
            if (['UAE', 'Qatar', 'Saudi Arabia'].includes(dest)) baseFee = 95;
            document.getElementById('resultFee').textContent = `$${baseFee} USD Approx Govt Processing Fee`;

            const docs = [
                `Valid ${passType} (Minimum 6 months validity from departure date)`,
                `Biometric passport photos meeting ${dest} embassy guidelines`,
                `Bank statements (Last 3 to 6 months)`,
                `Hotel accommodation booking / proof of stay`,
                `Round-trip flight ticket reservation`,
                `Official statement of purpose for ${vType}`
            ];
            document.getElementById('docList').innerHTML = docs.map(d => `<li class="flex items-start gap-2"><i class="fa-solid fa-circle-check text-green-500 mt-1"></i> <span>${d}</span></li>`).join('');

            const terms = [
                `Maximum stay: Up to 90 days per entry`,
                `Overstaying incurs daily legal fines and potential travel restrictions`,
                `Mandatory travel insurance coverage required`,
                `Biometrics appointment required at designated center`
            ];
            document.getElementById('termsList').innerHTML = terms.map(t => `<li class="flex items-start gap-2"><i class="fa-solid fa-circle-exclamation text-brandRed mt-1"></i> <span>${t}</span></li>`).join('');

            document.getElementById('offerText').textContent = `Talk to an experienced agent live about your travel needs.`;

            resultsDiv.scrollIntoView({ behavior: 'smooth' });
        }

        function triggerHandledAssistance() {
            const origin = document.getElementById('visaOrigin').value || "Egypt";
            const dest = document.getElementById('visaDest').value || "Canada";
            const vType = document.getElementById('visaType').value || "Tourist Visa";
            openAssistanceModal(vType, dest);
        }

        // FLIGHT SEARCH LOGIC
        function toggleReturnDate(show) {
            const container = document.getElementById('returnDateContainer');
            if (show) container.classList.remove('opacity-40', 'pointer-events-none');
            else container.classList.add('opacity-40', 'pointer-events-none');
        }

        function runFlightSearch() {
            const origin = document.getElementById('flightOriginCity').value || "Cairo (CAI) - Egypt";
            const dest = document.getElementById('flightDestCity').value || "Toronto (YYZ) - Canada";

            const resultsContainer = document.getElementById('flightResults');
            const flightList = document.getElementById('flightList');
            resultsContainer.classList.remove('hidden');

            const airlines = [
                { name: "Emirates", logo: "fa-plane-up", price: "$620", stops: "1 Stop", time: "14h 20m" },
                { name: "Qatar Airways", logo: "fa-plane", price: "$645", stops: "1 Stop", time: "15h 05m" },
                { name: "Turkish Airlines", logo: "fa-plane-departure", price: "$590", stops: "1 Stop", time: "13h 45m" },
                { name: "Lufthansa / Air Canada", logo: "fa-plane", price: "$710", stops: "Direct Flight", time: "11h 30m" }
            ];

            const flightAffiliateLinks = document.getElementById('flightAffiliateLinks');
            flightAffiliateLinks.innerHTML = `
                <div class="sm:col-span-2 lg:col-span-4 mt-2 rounded-2xl border border-purple-200 bg-purple-50 p-4">
                    <h4 class="text-base font-black text-slate-900">Choose where to continue booking</h4>
                    <p class="text-xs text-slate-600 mt-1 mb-3">Compare these travel partners for your ${origin} → ${dest} trip.</p>
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
                        <a href="https://www.kiwi.com/en/" target="_blank" rel="noopener sponsored" class="w-full text-center px-3 py-3 rounded-xl bg-indigo-700 hover:bg-indigo-800 text-white font-bold text-xs"><img src="https://cdn.simpleicons.org/kiwi/ffffff" alt="Kiwi" class="h-5 w-5 mx-auto mb-1">Kiwi.com</a>
                        <a href="https://compensair.tpo.lu/zS2xTWji" target="_blank" rel="noopener sponsored" class="w-full text-center px-3 py-3 rounded-xl bg-sky-600 hover:bg-sky-700 text-white font-bold text-xs"><span class="block text-lg leading-5">✈</span>Compensair</a>
                        <a href="https://aviasales.tpo.lu/oQwLDucI" target="_blank" rel="noopener sponsored" class="w-full text-center px-3 py-3 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs"><img src="https://cdn.simpleicons.org/aviasales/ffffff" alt="Aviasales" class="h-5 w-5 mx-auto mb-1">Aviasales</a>
                        <a href="https://klook.tpo.lu/dNTBgDcE" target="_blank" rel="noopener sponsored" class="w-full text-center px-3 py-3 rounded-xl bg-orange-600 hover:bg-orange-700 text-white font-bold text-xs"><img src="https://cdn.simpleicons.org/klook/ffffff" alt="Klook" class="h-5 w-5 mx-auto mb-1">Klook</a>
                    </div>
                </div>`;

            flightList.innerHTML = airlines.map(a => `
                <div class="glass-card p-5 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4 border-l-4 border-l-brandRed">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 rounded-xl bg-brandNavy border border-brandRed/40 flex items-center justify-center text-brandRed text-xl">
                            <i class="fa-solid ${a.logo}"></i>
                        </div>
                        <div>
                            <div class="flex items-center gap-2">
                                <h4 class="text-base font-bold text-slate-900">${a.name}</h4>
                                <span class="bg-brandRed/20 text-brandRed text-[10px] font-bold px-2 py-0.5 rounded">${a.stops}</span>
                            </div>
                            <p class="text-xs text-slate-500 mt-1">${origin} ➔ ${dest} • Duration: ${a.time}</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-4 w-full md:w-auto justify-between md:justify-end border-t md:border-t-0 border-gray-800 pt-3 md:pt-0">
                        <div class="text-left md:text-right">
                            <span class="text-[10px] text-slate-500 uppercase block">Best Available Rate</span>
                            <span class="text-2xl font-black text-brandRed">${a.price}</span>
                        </div>
                        <a href="https://www.skyscanner.com" target="_blank" class="px-5 py-2.5 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 font-bold text-xs transition shadow-md flex items-center gap-1">
                            Book Deal <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
                        </a>
                    </div>
                </div>
            `).join('');

            resultsContainer.scrollIntoView({ behavior: 'smooth' });
        }

        // ACCOMMODATION SEARCH
        const sampleHotels = [
            { name: "The Ritz Luxury Resort", rating: "4.9 ★", price: 340, img: "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=600&q=80", tag: "Luxury Choice" },
            { name: "Grand Horizon Hotel & Spa", rating: "4.7 ★", price: 180, img: "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=600&q=80", tag: "Top Rated" },
            { name: "Urban City Boutique Stay", rating: "4.5 ★", price: 95, img: "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=600&q=80", tag: "Best Value" },
            { name: "Palace Waterfront Suites", rating: "4.8 ★", price: 520, img: "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=600&q=80", tag: "Exclusive" }
        ];

        function runHotelSearch() {
            document.getElementById('hotelResults').classList.remove('hidden');
            document.getElementById('hotelAffiliateLinks').innerHTML = `
                <div class="rounded-2xl border border-orange-200 bg-gradient-to-r from-orange-50 to-rose-50 p-5">
                    <h4 class="text-base font-black text-slate-900">Choose where to book your stay</h4>
                    <p class="text-xs text-slate-600 mt-1 mb-3">Continue with our accommodation partner for stays and destination activities.</p>
                    <a href="https://klook.tpo.lu/dNTBgDcE" target="_blank" rel="noopener sponsored" class="inline-flex w-full sm:w-auto justify-center items-center gap-2 px-5 py-3 rounded-xl bg-orange-600 hover:bg-orange-700 text-white font-bold text-xs">Book accommodation on Klook <i class="fa-solid fa-arrow-up-right-from-square"></i></a>
                </div>`;
            filterHotels();
            document.getElementById('hotelResults').scrollIntoView({ behavior: 'smooth' });
        }

        function filterHotels() {
            const maxPrice = parseInt(document.getElementById('priceRange').value);
            document.getElementById('priceRangeValue').textContent = `Up to $${maxPrice}/night`;

            const filtered = sampleHotels.filter(h => h.price <= maxPrice);
            document.getElementById('hotelCount').textContent = filtered.length;

            const list = document.getElementById('hotelList');
            if (filtered.length === 0) {
                list.innerHTML = `<div class="col-span-3 text-center py-8 text-slate-500">No accommodations found under $${maxPrice}. Adjust the filter.</div>`;
                return;
            }

            list.innerHTML = filtered.map(h => `
                <div class="glass-card rounded-2xl overflow-hidden glass-card-hover flex flex-col justify-between">
                    <div>
                        <div class="relative h-48 overflow-hidden">
                            <img src="${h.img}" alt="${h.name}" class="w-full h-full object-cover">
                            <span class="absolute top-3 left-3 bg-white border border-brandRed/40 text-brandRed text-[10px] font-extrabold px-2 py-1 rounded-md uppercase tracking-wider">${h.tag}</span>
                            <span class="absolute bottom-3 right-3 bg-white text-yellow-400 font-bold text-xs px-2 py-1 rounded-md">${h.rating}</span>
                        </div>
                        <div class="p-5">
                            <h4 class="text-lg font-bold text-slate-900">${h.name}</h4>
                            <p class="text-xs text-slate-500 mt-1"><i class="fa-solid fa-wifi text-brandRed"></i> Free High-Speed WiFi • Pool • Airport Transfer</p>
                        </div>
                    </div>
                    <div class="p-5 pt-0 flex items-center justify-between border-t border-gray-800/80 mt-2">
                        <div>
                            <span class="text-[10px] text-slate-500 block">Nightly Rate</span>
                            <span class="text-xl font-black text-brandRed">$${h.price} <span class="text-xs text-slate-500 font-normal">/ night</span></span>
                        </div>
                        <a href="https://www.booking.com" target="_blank" class="px-4 py-2 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 text-xs font-bold transition">
                            Reserve Room
                        </a>
                    </div>
                </div>
            `).join('');
        }

        // MAP LOGIC
        let leafletMap = null;
        let markers = [];

        function initMap() {
            leafletMap = L.map('map').setView([30.0444, 31.2357], 12);
            L.tileLayer('https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=cb1_4gsq_1_d8b88cfd3d21c08926656aa9', {
                attribution: '&copy; OpenStreetMap &copy; CARTO',
                maxZoom: 19
            }).addTo(leafletMap);
        }

        function runGroundSearch() {
            const location = document.getElementById('groundLocation').value || "Cairo";
            const service = document.getElementById('groundService').value;

            const groundAffiliateLinks = document.getElementById('groundAffiliateLinks');
            groundAffiliateLinks.innerHTML = `
                <div class="sm:col-span-3 mb-1">
                    <span class="text-purple-600 text-xs font-extrabold uppercase tracking-widest">Move with confidence</span>
                    <h3 class="text-2xl font-black text-slate-900 mt-1">Choose the help you need in ${location}</h3>
                    <p class="text-sm text-slate-600 mt-1">Compare a few practical ways to get around once you arrive.</p>
                </div>
                <a href="https://gettransfer.tpo.lu/VKCddkka" target="_blank" rel="noopener sponsored" class="group relative overflow-hidden rounded-2xl min-h-[190px] p-5 flex flex-col justify-end text-white shadow-lg bg-cover bg-center" style="background-image:linear-gradient(0deg,rgba(3,78,63,.94),rgba(3,78,63,.12)),url('https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=900&q=85')">
                    <span class="relative text-[10px] font-extrabold uppercase tracking-widest text-emerald-200">Airport pickup</span>
                    <h4 class="relative text-xl font-black mt-1">Start your arrival smoothly</h4>
                    <span class="relative inline-flex items-center gap-2 mt-3 text-xs font-bold">Book GetTransfer <i class="fa-solid fa-arrow-up-right-from-square"></i></span>
                </a>
                <a href="https://klook.tpo.lu/dNTBgDcE" target="_blank" rel="noopener sponsored" class="group relative overflow-hidden rounded-2xl min-h-[190px] p-5 flex flex-col justify-end text-white shadow-lg bg-cover bg-center" style="background-image:linear-gradient(0deg,rgba(106,39,4,.94),rgba(106,39,4,.10)),url('https://images.unsplash.com/photo-1473448912268-2022ce9509d8?auto=format&fit=crop&w=900&q=85')">
                    <span class="relative text-[10px] font-extrabold uppercase tracking-widest text-amber-200">Domestic transportation</span>
                    <h4 class="relative text-xl font-black mt-1">Explore more of the country</h4>
                    <span class="relative inline-flex items-center gap-2 mt-3 text-xs font-bold">Explore Klook <i class="fa-solid fa-arrow-up-right-from-square"></i></span>
                </a>
                <a href="https://kiwitaxi.tpo.lu/FEwN4rkU" target="_blank" rel="noopener sponsored" class="group relative overflow-hidden rounded-2xl min-h-[190px] p-5 flex flex-col justify-end text-white shadow-lg bg-cover bg-center" style="background-image:linear-gradient(0deg,rgba(30,41,59,.94),rgba(30,41,59,.10)),url('https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&w=900&q=85')">
                    <span class="relative text-[10px] font-extrabold uppercase tracking-widest text-slate-200">Taxi</span>
                    <h4 class="relative text-xl font-black mt-1">Get there without the guesswork</h4>
                    <span class="relative inline-flex items-center gap-2 mt-3 text-xs font-bold">Find a Kiwitaxi ride <i class="fa-solid fa-arrow-up-right-from-square"></i></span>
                </a>
            `;

            leafletMap.setView([30.0444 + (Math.random()-0.5)*0.04, 31.2357 + (Math.random()-0.5)*0.04], 13);
            markers.forEach(m => leafletMap.removeLayer(m));
            markers = [];

            const marker = L.marker([30.0444, 31.2357]).addTo(leafletMap)
                .bindPopup(`<b>PamsBeyond Local Service Hub</b><br>${service} in ${location}`).openPopup();
            markers.push(marker);
        }

        // CHATBOT FUNCTIONS
        function toggleChatbot() {
            const chatBox = document.getElementById('chatBox');
            chatBox.classList.toggle('hidden');
        }

        function sendQuickMsg(text) {
            appendUserMsg(text);
            setTimeout(() => {
                appendOfficerMsg(`Thank you for inquiring about "${text}". An experienced officer is ready to help! You can click "Live Chat" or fill out our request form.`);
            }, 800);
        }

        function handleUserChat(e) {
            e.preventDefault();
            const input = document.getElementById('chatInput');
            const val = input.value.trim();
            if(!val) return;
            appendUserMsg(val);
            input.value = '';

            setTimeout(() => {
                appendOfficerMsg("Message received! Our human officers are processing your overseas travel request. Someone will reply directly or you can leave your email.");
            }, 1000);
        }

        function appendUserMsg(txt) {
            const chatMessages = document.getElementById('chatMessages');
            const msg = document.createElement('div');
            msg.className = "bg-brandRed text-slate-900 p-2.5 rounded-xl ml-auto max-w-[80%] text-right font-medium";
            msg.textContent = txt;
            chatMessages.appendChild(msg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function appendOfficerMsg(txt) {
            const chatMessages = document.getElementById('chatMessages');
            const msg = document.createElement('div');
            msg.className = "bg-brandGray border border-gray-800 p-2.5 rounded-xl mr-auto max-w-[85%] text-gray-200";
            msg.textContent = txt;
            chatMessages.appendChild(msg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        // MODAL FUNCTIONS
        function openAssistanceModal(visaType = "Tourist Visa", dest = "Flights") {
            document.getElementById('modalVisaType').value = visaType;
            const serviceSelect = document.getElementById('modalDest');
            serviceSelect.value = ['Flights', 'Hotels'].includes(dest) ? dest : 'Flights';
            document.getElementById('assistanceModal').classList.remove('hidden');
            document.getElementById('modalSuccess').classList.add('hidden');
            document.getElementById('assistanceForm').classList.remove('hidden');
        }

        function closeAssistanceModal() {
            document.getElementById('assistanceModal').classList.add('hidden');
        }

        async function handleAssistanceSubmit(e) {
            e.preventDefault();

            const name = document.getElementById('clientName').value.trim();
            const email = document.getElementById('clientEmail').value.trim();
            const visaType = document.getElementById('modalVisaType').value;
            const dest = document.getElementById('modalDest').value;
            const submitButton = document.querySelector('#assistanceForm button[type="submit"]');

            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sending...';

            const formData = {
                name,
                email,
                visa_assistance: visaType,
                other_service: dest,
                _subject: `PamsBeyond Officer Request: ${visaType} - ${dest}`,
                _captcha: 'true',
                _template: 'table'
            };

            try {
                const response = await fetch('https://formsubmit.co/ajax/pamsbeyond@gmail.com', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (!response.ok) {
                    throw new Error('Form submission failed');
                }

                document.getElementById('assistanceForm').classList.add('hidden');
                document.getElementById('modalSuccess').classList.remove('hidden');
            } catch (error) {
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Connect With Officer Desk';
                alert('Sorry, your request could not be sent. Please try again or email us directly.');
            }
        }

        // FLYING PLANES BACKGROUND CANVAS
        function initCanvas() {
            const canvas = document.getElementById('bgCanvas');
            const ctx = canvas.getContext('2d');

            function resize() {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }
            window.addEventListener('resize', resize);
            resize();

            const planes = Array.from({ length: 8 }, () => ({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                speed: 1 + Math.random() * 1.5,
                angle: Math.random() * Math.PI * 2,
                size: 10 + Math.random() * 8,
                trail: []
            }));

            function drawPlane(x, y, angle, size) {
                ctx.save();
                ctx.translate(x, y);
                ctx.rotate(angle);
                
                ctx.beginPath();
                ctx.moveTo(size * 1.5, 0);
                ctx.lineTo(-size, -size * 0.7);
                ctx.lineTo(-size * 0.4, 0);
                ctx.lineTo(-size, size * 0.7);
                ctx.closePath();
                ctx.fillStyle = '#e60023';
                ctx.fill();

                ctx.restore();
            }

            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                ctx.strokeStyle = 'rgba(230, 0, 35, 0.03)';
                ctx.lineWidth = 1;
                for (let x = 0; x < canvas.width; x += 60) {
                    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
                }

                planes.forEach(p => {
                    p.x += Math.cos(p.angle) * p.speed;
                    p.y += Math.sin(p.angle) * p.speed;

                    p.trail.push({ x: p.x, y: p.y });
                    if (p.trail.length > 20) p.trail.shift();

                    if (p.trail.length > 1) {
                        ctx.beginPath();
                        ctx.moveTo(p.trail[0].x, p.trail[0].y);
                        for (let i = 1; i < p.trail.length; i++) {
                            ctx.lineTo(p.trail[i].x, p.trail[i].y);
                        }
                        ctx.strokeStyle = 'rgba(230, 0, 35, 0.25)';
                        ctx.lineWidth = 1.5;
                        ctx.stroke();
                    }

                    if (p.x < -50) p.x = canvas.width + 50;
                    if (p.x > canvas.width + 50) p.x = -50;
                    if (p.y < -50) p.y = canvas.height + 50;
                    if (p.y > canvas.height + 50) p.y = -50;

                    drawPlane(p.x, p.y, p.angle, p.size);
                });

                requestAnimationFrame(animate);
            }

            animate();
        }
    </script>
</body>
</html>
"""

# Embed the uploaded PamsBeyond logo directly so the app works as a standalone app.py.
# Embed a standalone PamsBeyond logo so the app works without extra assets.
logo_data = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5MDAgMzAwIj4KPHJlY3Qgd2lkdGg9IjkwMCIgaGVpZ2h0PSIzMDAiIHJ4PSIyOCIgZmlsbD0iIzA4MDgwYSIvPgo8cGF0aCBkPSJNOTAgMjE4IEMxNjUgODAgMjQ1IDgwIDMyMCAxNjAgQzM4NSAyMjggNDcwIDIyMCA1NDAgMTMwIiBmaWxsPSJub25lIiBzdHJva2U9IiNlNjAwMjMiIHN0cm9rZS13aWR0aD0iMTIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8cGF0aCBkPSJNNDkyIDExNiBsMTUwIC01NSAtNTQgNTIgODQgMTggLTEwNCA5IC0zNiA1MCA0IC00OCAtNzAgLTI2IDc4IDR6IiBmaWxsPSIjZmZmIi8+Cjx0ZXh0IHg9IjcwIiB5PSIxNjUiIGZvbnQtZmFtaWx5PSJBcmlhbCxIZWx2ZXRpY2Esc2Fucy1zZXJpZiIgZm9udC1zaXplPSI4MiIgZm9udC13ZWlnaHQ9IjgwMCIgZmlsbD0iI2U2MDAyMyI+UGFtczwvdGV4dD4KPHRleHQgeD0iMzE1IiB5PSIxNjUiIGZvbnQtZmFtaWx5PSJBcmlhbCxIZWx2ZXRpY2Esc2Fucy1zZXJpZiIgZm9udC1zaXplPSI4MiIgZm9udC13ZWlnaHQ9IjgwMCIgZmlsbD0iI2ZmZiI+YmV5b25kPC90ZXh0Pgo8dGV4dCB4PSI3NCIgeT0iMjQyIiBmb250LWZhbWlseT0iQXJpYWwsSGVsdmV0aWNhLHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMzAiIGZvbnQtd2VpZ2h0PSI3MDAiIGxldHRlci1zcGFjaW5nPSI4IiBmaWxsPSIjZTYwMDIzIj5HRVQgQkVZT05EPC90ZXh0Pgo8L3N2Zz4="


# Product Hunt promotion
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🚀 We are live on Product Hunt!")
    st.markdown(
        """
        <div style="text-align: center;">
            <a href="https://producthunt.com" target="_blank" rel="noopener sponsored">
                <img src="https://producthunt.com"
                     alt="PamsBeyond - Intelligent all-in-one AI travel workspace"
                     style="width: 250px; height: 54px;" width="250" height="54" />
            </a>
            <p style="font-size: 14px; margin-top: 8px; color: #555;">
                If you love PamsBeyond, please support us with an upvote! 🙏
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

# Render Embedded Web App Component
components.html(html_code.replace("{{LOGO_DATA}}", logo_data), height=950, scrolling=True)

# -----------------------------------------------------------------------------
# Global Visa Requirements Hub
# -----------------------------------------------------------------------------
st.markdown("---")
st.title("🛂 PamsBeyond Global Visa Assistant")
st.write("Check passport and destination requirements from the local global visa dataset.")

@st.cache_data
def load_global_visa_data():
    visa_path = Path(__file__).with_name("passport-index-tidy.csv")
    if not visa_path.exists():
        return None
    data = pd.read_csv(visa_path)
    data.columns = data.columns.str.strip()
    required_columns = {"Passport", "Destination", "Requirement"}
    if not required_columns.issubset(data.columns):
        missing = ", ".join(sorted(required_columns - set(data.columns)))
        st.error(f"The visa dataset is missing required columns: {missing}.")
        return None
    return data

visa_df = load_global_visa_data()
if visa_df is None:
    st.info("Add `passport-index-tidy.csv` beside `app.py` to enable the 199-country visa lookup.")
else:
    passport_list = sorted(visa_df["Passport"].dropna().astype(str).unique())
    if not passport_list:
        st.warning("The visa dataset does not contain any passport records yet.")
    else:
        visa_col1, visa_col2 = st.columns(2)
        with visa_col1:
            passport = st.selectbox("Select your passport (citizenship)", passport_list, key="visa_hub_passport")
        filtered_visa_df = visa_df[visa_df["Passport"].astype(str) == passport]
        destination_list = sorted(filtered_visa_df["Destination"].dropna().astype(str).unique())
        with visa_col2:
            destination = st.selectbox("Select travel destination", destination_list, key="visa_hub_destination")

        if st.button("Check rules & restrictions 🔍", key="visa_hub_check"):
            match_row = filtered_visa_df[filtered_visa_df["Destination"].astype(str) == destination]
            if match_row.empty:
                st.error("No record found for this passport and destination combination.")
            else:
                requirement = str(match_row["Requirement"].iloc[0]).strip()
                normalized_requirement = requirement.lower()
                if normalized_requirement in {"visa free", "visa-free"}:
                    st.success(f"### 😎 Visa status: {requirement.title()}")
                    st.info("💡 Safe travels! You may not need a formal visa beforehand. Check maximum stay limits and current official entry rules.")
                elif normalized_requirement in {"e-visa", "visa on arrival", "voa", "eta"}:
                    st.warning(f"### ⚠️ Visa status: {requirement.title()}")
                    st.write("🎉 **Great news!** Review your documentation requirements online or before arrival.")
                    st.markdown("### 📑 Speed up your application with premium support")
                    st.write("Get a customized document-validation toolkit for your travel application.")
                    col_saas, col_info = st.columns(2)
                    with col_saas:
                        st.link_button("⭐ Unlock Priority Guides", "https://forms.gle/edZnKkHYAiWi9QxG7", use_container_width=True)
                    with col_info:
                        st.caption("Always confirm current requirements with the destination's official embassy, consulate, or immigration authority.")
                else:
                    st.error(f"### 🛑 Visa status: {requirement.title()}")
                    st.info("📋 **Action required:** Coordinate with the destination's official embassy or consulate before booking your departure.")

# -----------------------------------------------------------------------------
# Native Trip Planner workspace
# -----------------------------------------------------------------------------
st.markdown("---")
st.title("🧭 Trip Planner")
st.caption("Build a route, understand the real budget, check your packing progress, and download a polished trip portfolio.")

THEMES = {
    "Classic Navy": {"primary": "#1e3a8a", "light": "#edf2f7", "accent": "#f8fafc", "plotly": "Blues"},
    "Emerald Adventure": {"primary": "#064e3b", "light": "#e6f4ea", "accent": "#f4fbf7", "plotly": "Greens"},
    "Sunset Burgundy": {"primary": "#7f1d1d", "light": "#fff1f2", "accent": "#fff7ed", "plotly": "Reds"},
}

with st.sidebar:
    st.header("Trip Planner Settings")
    theme_choice = st.selectbox("Brand palette", list(THEMES), key="planner_theme")
    selected_theme = THEMES[theme_choice]
    st.caption("Your plan stays in this session unless you export it.")

if "planner_cities" not in st.session_state:
    st.session_state.planner_cities = [
        {"name": "London, UK", "days": 3, "transit": "✈️ International flight"},
        {"name": "Paris, France", "days": 4, "transit": "🚄 High-speed train"},
    ]
if "planner_packing" not in st.session_state:
    st.session_state.planner_packing = [
        {"item": "Valid passport and visa printouts", "checked": True},
        {"item": "Universal power adapter", "checked": True},
        {"item": "Prescription medication and first aid", "checked": False},
        {"item": "Comfortable walking shoes", "checked": False},
    ]
if "planner_feedback" not in st.session_state:
    st.session_state.planner_feedback = []

planner_state = {
    "cities": st.session_state.planner_cities,
    "packing_items": st.session_state.planner_packing,
    "theme": theme_choice,
}
with st.sidebar:
    st.download_button(
        "📤 Export plan backup (.json)",
        data=json.dumps(planner_state, indent=2),
        file_name="pamsbeyond-travel-plan.json",
        mime="application/json",
        use_container_width=True,
    )
    uploaded_plan = st.file_uploader("📥 Import a previous plan", type=["json"], key="planner_import")
    if uploaded_plan is not None and st.button("Load imported plan", use_container_width=True):
        try:
            loaded = json.load(uploaded_plan)
            if isinstance(loaded.get("cities"), list) and isinstance(loaded.get("packing_items"), list):
                st.session_state.planner_cities = loaded["cities"]
                st.session_state.planner_packing = loaded["packing_items"]
                st.success("Plan loaded.")
                st.rerun()
        except (json.JSONDecodeError, AttributeError):
            st.error("That file is not a valid PamsBeyond plan backup.")

planner_tab1, planner_tab2, planner_tab3 = st.tabs(["🗺️ Route & budget", "🎒 Checklist & notes", "📊 Results & export"])

with planner_tab1:
    route_col, budget_col = st.columns(2)
    with route_col:
        st.subheader("Multi-city route")
        action_col1, action_col2 = st.columns(2)
        with action_col1:
            if st.button("➕ Add destination", use_container_width=True):
                st.session_state.planner_cities.append({"name": "New city stop", "days": 1, "transit": "✈️ Flight"})
                st.rerun()
        with action_col2:
            if st.button("➖ Remove last", use_container_width=True) and len(st.session_state.planner_cities) > 1:
                st.session_state.planner_cities.pop()
                st.rerun()
        transit_options = ["✈️ International flight", "🚄 High-speed train", "🚗 Rental car / drive", "🚌 Intercity bus", "⚓ Ferry / cruise"]
        for idx, city in enumerate(st.session_state.planner_cities):
            c1, c2, c3 = st.columns([2, 1, 2])
            with c1:
                city["name"] = st.text_input(f"City #{idx + 1}", value=city.get("name", ""), key=f"planner_city_{idx}")
            with c2:
                city["days"] = st.number_input("Days", min_value=1, max_value=60, value=int(city.get("days", 1)), key=f"planner_days_{idx}")
            with c3:
                current = city.get("transit", transit_options[0])
                city["transit"] = st.selectbox("Arrival transit", transit_options, index=transit_options.index(current) if current in transit_options else 0, key=f"planner_transit_{idx}")
        total_days = sum(int(city["days"]) for city in st.session_state.planner_cities)
        st.metric("Total trip duration", f"{total_days} days")

    with budget_col:
        st.subheader("Budget builder")
        currency = st.selectbox("Currency", ["$", "€", "£", "AED", "SAR", "EGP", "¥"], key="planner_currency")
        travelers = st.number_input("Travelers", min_value=1, max_value=50, value=2, key="planner_travelers")
        b1, b2 = st.columns(2)
        with b1:
            flight_cost = st.number_input(f"Transport per person ({currency})", min_value=0.0, value=450.0, key="planner_flights")
            hotel_cost = st.number_input(f"Hotel per night ({currency})", min_value=0.0, value=120.0, key="planner_hotels")
        with b2:
            daily_cost = st.number_input(f"Food + local transit per person/day ({currency})", min_value=0.0, value=65.0, key="planner_daily")
            other_costs = st.number_input(f"Other fixed costs ({currency})", min_value=0.0, value=150.0, key="planner_other")
        buffer_label = st.select_slider("Emergency buffer", options=["Standard (10%)", "Enhanced (15%)", "Max security (25%)"], value="Enhanced (15%)", key="planner_buffer")
        buffer_rate = 0.10 if "10%" in buffer_label else 0.15 if "15%" in buffer_label else 0.25
        alt_currency = st.text_input("Alternative currency label", "EUR", key="planner_alt_currency")
        exchange_rate = st.number_input(f"1 {currency} equals how many {alt_currency}?", min_value=0.0001, value=0.82, format="%.4f", key="planner_exchange")

with planner_tab2:
    checklist_col, notes_col = st.columns(2)
    with checklist_col:
        st.subheader("Packing checklist")
        new_item = st.text_input("Add a custom item", placeholder="Example: camera charger", key="planner_new_item")
        if st.button("Add item", key="planner_add_item") and new_item.strip():
            st.session_state.planner_packing.append({"item": new_item.strip(), "checked": False})
            st.rerun()
        for idx, item in enumerate(st.session_state.planner_packing):
            item["checked"] = st.checkbox(item["item"], value=bool(item.get("checked", False)), key=f"planner_pack_{idx}")
        packed = sum(1 for item in st.session_state.planner_packing if item["checked"])
        total_items = len(st.session_state.planner_packing)
        progress = (packed / total_items * 100) if total_items else 0
        st.progress(progress / 100, text=f"{packed} of {total_items} packed ({progress:.0f}%)")
        progress_fig = px.bar(pd.DataFrame({"Status": ["Packed"], "Percentage": [progress]}), x="Percentage", y="Status", orientation="h", range_x=[0, 100], text_auto=".0f", color_discrete_sequence=[selected_theme["primary"]], height=130)
        progress_fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), xaxis_title="Percent complete", yaxis_title="")
        st.plotly_chart(progress_fig, use_container_width=True, key="planner_progress_chart")
    with notes_col:
        st.subheader("Trip notes")
        trip_notes = st.text_area("Flight details, reservations, reminders", value="Double-check passport validity, confirmations, and official entry requirements before departure.", height=220, key="planner_notes")

with planner_tab3:
    nights = max(1, total_days - 1)
    transport_total = flight_cost * travelers
    hotels_total = hotel_cost * nights
    daily_total = daily_cost * total_days * travelers
    subtotal = transport_total + hotels_total + daily_total + other_costs
    emergency_fund = subtotal * buffer_rate
    grand_total = subtotal + emergency_fund
    per_person = grand_total / travelers
    converted_total = grand_total * exchange_rate
    metrics_col, chart_col = st.columns([1, 1])
    with metrics_col:
        st.subheader("Live budget overview")
        st.metric("Base subtotal", f"{currency}{subtotal:,.2f}")
        st.metric("Emergency fund", f"{currency}{emergency_fund:,.2f}")
        st.metric("Grand total", f"{currency}{grand_total:,.2f}")
        st.metric(f"Total in {alt_currency}", f"{converted_total:,.2f} {alt_currency}")
        st.metric("Cost per person", f"{currency}{per_person:,.2f}")
    with chart_col:
        st.subheader("Budget distribution")
        budget_df = pd.DataFrame({"Category": ["Transport", "Hotels", "Food + local transit", "Other fixed", "Emergency fund"], "Cost": [transport_total, hotels_total, daily_total, other_costs, emergency_fund]})
        fig = px.pie(budget_df, values="Cost", names="Category", hole=0.42, color_discrete_sequence=px.colors.sequential.__dict__.get(selected_theme["plotly"], px.colors.sequential.Blues))
        fig.update_layout(margin=dict(t=30, b=10, l=10, r=10), legend_title_text="")
        st.plotly_chart(fig, use_container_width=True, key="planner_budget_chart")

    def generate_trip_pdf():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm, topMargin=16 * mm, bottomMargin=16 * mm, title="PamsBeyond Travel Portfolio")
        styles = getSampleStyleSheet()
        heading = ParagraphStyle("TripHeading", parent=styles["Heading2"], textColor=colors.HexColor(selected_theme["primary"]), spaceBefore=10, spaceAfter=5)
        story = [Paragraph("PamsBeyond Travel Portfolio", styles["Title"]), Paragraph(f"{total_days} days · {travelers} traveler(s) · Total: {currency}{grand_total:,.2f}", styles["Normal"]), Paragraph("Route", heading)]
        for idx, city in enumerate(st.session_state.planner_cities, 1):
            story.append(Paragraph(f"Stop {idx}: {city['name']} — {city['days']} day(s) via {city['transit']}", styles["BodyText"]))
        story += [Paragraph("Budget summary", heading)]
        table_data = [["Category", f"Cost ({currency})"], ["Transport", f"{transport_total:,.2f}"], ["Hotels", f"{hotels_total:,.2f}"], ["Food + local transit", f"{daily_total:,.2f}"], ["Other fixed", f"{other_costs:,.2f}"], [f"Emergency fund ({int(buffer_rate * 100)}%)", f"{emergency_fund:,.2f}"], ["Grand total", f"{grand_total:,.2f}"]]
        table = Table(table_data, colWidths=[280, 120])
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(selected_theme["primary"])), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")), ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor(selected_theme["light"])), ("PADDING", (0, 0), (-1, -1), 7)]))
        story.append(table)
        story.append(Paragraph("Packing checklist", heading))
        for item in st.session_state.planner_packing:
            story.append(Paragraph(f"{'[X]' if item['checked'] else '[ ]'} {item['item']}", styles["BodyText"]))
        if trip_notes.strip():
            story += [Paragraph("Trip notes", heading), Paragraph(trip_notes.replace("&", "&amp;").replace("\n", "<br/>"), styles["BodyText"])]
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    st.download_button("📄 Download full travel portfolio PDF", data=generate_trip_pdf(), file_name="PamsBeyond_Travel_Portfolio.pdf", mime="application/pdf", use_container_width=True)


with st.sidebar:
    st.divider()
    st.header("Rate the planner")
    with st.form("planner_feedback_form", clear_on_submit=True):
        rating = st.slider("Rating", 1, 5, 5)
        feedback = st.text_area("Optional feedback")
        if st.form_submit_button("Submit review"):
            st.session_state.planner_feedback.append({"rating": rating, "feedback": feedback.strip() or "No written feedback."})
            st.success("Thanks for helping us improve.")

# --- B2B SAAS WHITE-LABEL VALIDATION PANEL ---
with st.sidebar:
    st.divider()
    st.write("💼 **PamsBeyond for Business**")
    st.caption(
        "Are you an independent travel agent, tour operator, or retreat organizer? "
        "Stop manually formatting trip spreadsheets for your clients."
    )

    with st.expander("✨ Build Custom Portfolios"):
        st.markdown(
            "We are building a **White-Label Premium SaaS version** of PamsBeyond! "
            "You will be able to:\n"
            "* 🚫 Remove all PamsBeyond branding\n"
            "* 🖼️ Upload your own custom agency logo\n"
            "* 🎨 Customize UI colors to match your brand\n"
            "* 📄 Instantly generate custom PDF itineraries for your clients"
        )

        business_form_url = "https://forms.gle/edZnKkHYAiWi9QxG7"
        st.markdown(
            f'<a href="{business_form_url}" target="_blank" rel="noopener noreferrer">'
            f'<button style="width:100%; background-color:#4A90E2; color:white; border:none; '
            f'padding:10px; border-radius:5px; cursor:pointer; font-weight:bold;">'
            f'🚀 Join Private Agency Beta</button></a>',
            unsafe_allow_html=True,
        )

# Visible fallback for mobile layouts where the Streamlit sidebar is collapsed.
st.markdown("---")
st.subheader("💼 PamsBeyond for Business")
st.write("Are you a travel agent, tour operator, or retreat organizer? Build branded client portfolios faster.")
st.link_button("🚀 Join Private Agency Beta", "https://forms.gle/edZnKkHYAiWi9QxG7", use_container_width=True)
