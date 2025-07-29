#!/usr/bin/env python3
"""
yt-dlp MCP Server

Provides YouTube video operations through MCP protocol.
"""

import json
import re
import tempfile
import os
import sys
import io
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

import yt_dlp
from fastmcp import FastMCP


# Initialize FastMCP
mcp = FastMCP("yt-dlp-mcp")


class YouTubeDownloader:
    """Helper class for YouTube operations using yt-dlp"""
    
    def __init__(self):
        self.base_opts = {
            'quiet': True,
            'no_warnings': True,
            'extractaudio': False,
            'audioformat': 'mp3',
            'outtmpl': '%(title)s.%(ext)s',
            'noprogress': True,  # Disable progress output
            'no_color': True,    # Disable colored output
            'logger': self._get_null_logger(),  # Use null logger
        }
    
    def _get_null_logger(self):
        """Return a null logger to suppress all yt-dlp output"""
        logger = logging.getLogger('yt-dlp-null')
        logger.setLevel(logging.CRITICAL + 1)  # Disable all logging
        return logger
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Extract video information without downloading"""
        opts = self.base_opts.copy()
        opts.update({
            'skip_download': True,
            'writesubtitles': False,
            'writeautomaticsub': False,        })
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return info
            except Exception as e:
                raise Exception(f"Failed to extract video info: {str(e)}")
    
    def get_transcription(self, url: str, keep_timestamps: bool = False) -> str:
        """Extract transcription from YouTube video"""
        # Redirect stdout and stderr to suppress yt-dlp output
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                opts = self.base_opts.copy()
                opts.update({
                    'skip_download': True,
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['en'],  # Only download English subtitles to avoid duplicates
                    'subtitlesformat': 'vtt',
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                })
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    try:
                        info = ydl.extract_info(url, download=False)
                        video_id = info.get('id', 'video')
                        video_title = info.get('title', 'Unknown Title')
                        
                        # Process the video to get subtitles
                        ydl.process_info(info)
                        
                        # Look for subtitle files
                        subtitle_files = []
                        for file in Path(temp_dir).glob('*.vtt'):
                            subtitle_files.append(file)
                        
                        if not subtitle_files:
                            return f"No transcription available for video: {video_title}"
                          # Process the first available subtitle file
                        subtitle_file = subtitle_files[0]
                        transcription = self._process_vtt_file(subtitle_file, keep_timestamps)
                        
                        return f"Transcription for '{video_title}':\n\n{transcription}"
                        
                    except Exception as e:
                        raise Exception(f"Failed to extract transcription: {str(e)}")
        finally:
            # Restore stdout and stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def _process_vtt_file(self, vtt_file: Path, keep_timestamps: bool) -> str:
        """Process VTT subtitle file to extract text"""
        try:
            with open(vtt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            transcription_lines = []
            seen_lines = set()  # Track seen lines to prevent duplicates
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Skip VTT header and empty lines
                if not line or line.startswith('WEBVTT') or line.startswith('NOTE'):
                    continue
                
                # Check if line contains timestamp
                if '-->' in line:
                    if keep_timestamps:
                        transcription_lines.append(f"[{line}]")
                    continue
                
                # Skip cue settings and add actual text
                if not re.match(r'^[\d:.,\s\-\>]+$', line) and line:
                    # Clean up HTML tags and formatting
                    clean_line = re.sub(r'<[^>]+>', '', line)
                    clean_line = clean_line.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                    clean_line = clean_line.strip()
                    
                    # Only add if the line is not empty and hasn't been seen before
                    if clean_line and clean_line not in seen_lines:
                        seen_lines.add(clean_line)
                        transcription_lines.append(clean_line)
            
            return '\n'.join(transcription_lines)
            
        except Exception as e:
            return f"Error processing subtitle file: {str(e)}"


@mcp.tool()
def get_transcription(url: str, keep_timestamps: bool = False) -> str:
    """
    Extract transcription from a YouTube video.
    
    Args:
        url: YouTube video URL
        keep_timestamps: Whether to keep timestamp information in the transcription
    
    Returns:
        Video transcription text
    """
    try:
        downloader = YouTubeDownloader()
        return downloader.get_transcription(url, keep_timestamps)
    except Exception as e:
        return f"Error getting transcription: {str(e)}"


@mcp.tool()
def search_videos(search_terms: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Search for YouTube videos by terms and return video information.
    
    Args:
        search_terms: Search query for YouTube videos
        max_results: Maximum number of results to return (default: 10)
    
    Returns:
        List of dictionaries containing video title, URL, and description
    """
    try:
        # Use yt-dlp to search for videos
        search_url = f"ytsearch{max_results}:{search_terms}"
        
        downloader = YouTubeDownloader()
        opts = downloader.base_opts.copy()
        opts.update({
            'extract_flat': True,  # Only extract basic info, don't download
            'quiet': True,
        })
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            search_results = ydl.extract_info(search_url, download=False)
            
            if not search_results or 'entries' not in search_results:
                return [{"error": "No search results found"}]
            
            video_list = []
            for entry in search_results['entries']:
                if entry:  # Some entries might be None
                    video_info = {
                        'title': entry.get('title', 'Unknown Title'),
                        'url': entry.get('url', entry.get('webpage_url', '')),
                        'description': entry.get('description', '')[:200] + '...' if entry.get('description') else '',
                        'duration': str(entry.get('duration', 'Unknown')),
                        'views': str(entry.get('view_count', 'Unknown')),
                        'channel': entry.get('uploader', 'Unknown Channel')
                    }
                    video_list.append(video_info)
            
            return video_list
            
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]


@mcp.tool()
def list_channel_videos(channel_identifier: str, max_videos: int = 10) -> List[Dict[str, str]]:
    """
    List recent videos from a YouTube channel.
    
    Args:
        channel_identifier: Channel name, URL, or handle (e.g., "@channelname" or "UC...")
        max_videos: Number of recent videos to return (default: 10)
    
    Returns:
        List of dictionaries containing video information from the channel
    """
    try:
        # Handle different channel identifier formats
        if channel_identifier.startswith('http'):
            # Direct URL
            channel_url = channel_identifier
        elif channel_identifier.startswith('@'):
            # Handle format
            channel_url = f"https://www.youtube.com/{channel_identifier}"
        elif channel_identifier.startswith('UC') or channel_identifier.startswith('UU'):
            # Channel ID
            channel_url = f"https://www.youtube.com/channel/{channel_identifier}"
        else:
            # Try searching for the channel name
            search_url = f"ytsearch1:{channel_identifier} channel"
            downloader = YouTubeDownloader()
            opts = downloader.base_opts.copy()
            opts.update({'extract_flat': True, 'quiet': True})
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                search_results = ydl.extract_info(search_url, download=False)
                if not search_results or 'entries' not in search_results or not search_results['entries']:
                    return [{"error": f"Channel '{channel_identifier}' not found"}]
                
                # Get the channel URL from the first video
                first_entry = search_results['entries'][0]
                if first_entry and 'channel_url' in first_entry:
                    channel_url = first_entry['channel_url']
                else:
                    return [{"error": f"Could not find channel for '{channel_identifier}'"}]
        
        # Extract channel videos using yt-dlp
        # Use the channel URL with videos suffix to get recent videos
        if '/channel/' in channel_url:
            videos_url = channel_url + '/videos'
        elif '/@' in channel_url:
            videos_url = channel_url + '/videos'
        else:
            videos_url = channel_url + '/videos'
        
        downloader = YouTubeDownloader()
        opts = downloader.base_opts.copy()
        opts.update({
            'extract_flat': True,
            'quiet': True,
            'playlistend': max_videos,  # Limit the number of videos
        })
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                channel_info = ydl.extract_info(videos_url, download=False)
                
                if not channel_info or 'entries' not in channel_info:
                    return [{"error": f"Could not retrieve videos for channel '{channel_identifier}'"}]
                
                videos = []
                for entry in channel_info['entries']:
                    if entry and len(videos) < max_videos:  # Double-check the limit
                        video_info = {
                            'title': entry.get('title', 'Unknown Title'),
                            'url': entry.get('url', entry.get('webpage_url', '')),
                            'description': entry.get('description', '')[:200] + '...' if entry.get('description') else '',
                            'duration': str(entry.get('duration', 'Unknown')),
                            'views': str(entry.get('view_count', 'Unknown')),
                            'published': entry.get('upload_date', 'Unknown')
                        }
                        videos.append(video_info)
                
                return videos if videos else [{"error": "No videos found for this channel"}]
                
            except Exception as e:
                return [{"error": f"Failed to extract channel videos: {str(e)}"}]
        
    except Exception as e:
        return [{"error": f"Failed to list channel videos: {str(e)}"}]


def main():
    """Main entry point for the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
