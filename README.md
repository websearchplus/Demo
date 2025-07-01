# Web Search Plus Demo

Web Search Plus is a search tool specifically developed for LLM that can intelligently filter out invalid information.

Web Search is the most important tool of LLM. LLM needs to obtain real-time information through web search. However, excessive information with low relevance to the search topic interferes with the inference quality of LLM, causing hallucination and reducing its inference speed. At the same time, it also generates a large amount of ineffective inference costs

**The reop show how to use web search plus with mainstream agent framework, include  mcp server of web search plus**

## Prerequisites

- Python >= 3.12.0
- A valid Web Search Plus API key 
- A valid OpenAI API key

## Usage

- langchain_demo.py: OpenAI + Langchain(tool call) + Web Search Plus API
- openai_sdk_demo.py: OpenAI Python SDK + Web Search Plus API
- openai_agent_mcp: OpenAI Agent Python SDK + Web Search Plus MCP Server

## Setup Guide

Refer to [www.websearch.plus](https://www.websearch.plus/)

Get 4M tokens for free, no credit card required