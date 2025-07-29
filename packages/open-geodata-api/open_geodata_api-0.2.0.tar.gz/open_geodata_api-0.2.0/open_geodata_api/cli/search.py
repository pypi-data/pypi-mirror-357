"""
Search CLI commands with comprehensive help
"""
import click
import json
import open_geodata_api as ogapi


def parse_bbox(bbox_str):
    """Parse bbox string to list of floats."""
    try:
        bbox = [float(x.strip()) for x in bbox_str.split(',')]
        if len(bbox) != 4:
            raise ValueError("bbox must have exactly 4 values")
        return bbox
    except ValueError:
        raise click.BadParameter('bbox must be comma-separated numbers: west,south,east,north')


def parse_query(query_str):
    """Parse query string to dictionary."""
    try:
        return json.loads(query_str)
    except json.JSONDecodeError:
        raise click.BadParameter('query must be valid JSON string')


@click.group(name='search')
def search_group():
    """
    🔍 Search for satellite data items from various providers.
    
    Find satellite imagery and data products using spatial, temporal,
    and attribute filters. Supports both Planetary Computer and EarthSearch APIs.
    
    \b
    Common workflows:
    1. Quick search for recent data at a location
    2. Detailed search with multiple filters
    3. Export search results for later processing
    
    \b
    Examples:
      ogapi search quick sentinel-2-l2a "bbox"       # Quick recent search
      ogapi search items -c sentinel-2-l2a --bbox    # Detailed search
    """
    pass


@search_group.command('items')
@click.option('--provider', '-p',
              type=click.Choice(['pc', 'es'], case_sensitive=False),
              default='pc',
              help='Data provider (pc=Planetary Computer, es=EarthSearch)')
@click.option('--collections', '-c',
              required=True,
              help='Comma-separated collection names (e.g., "sentinel-2-l2a,landsat-c2-l2")')
@click.option('--bbox', '-b',
              callback=lambda ctx, param, value: parse_bbox(value) if value else None,
              help='Bounding box as "west,south,east,north" (e.g., "-122.5,47.5,-122.0,48.0")')
@click.option('--datetime', '-d',
              help='Date range as "YYYY-MM-DD/YYYY-MM-DD" or single date "YYYY-MM-DD"')
@click.option('--query', '-q',
              callback=lambda ctx, param, value: parse_query(value) if value else None,
              help='Filter query as JSON (e.g., \'{"eo:cloud_cover":{"lt":30}}\')')
@click.option('--limit', '-l',
              type=int,
              default=10,
              help='Maximum number of items to return (default: 10)')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save search results to JSON file for later processing')
@click.option('--show-assets/--no-assets',
              default=False,
              help='Display available assets/bands for each item')
@click.option('--cloud-cover', '-cc',
              type=float,
              help='Maximum cloud cover percentage (shortcut for common filter)')
@click.pass_context
def search_items(ctx, provider, collections, bbox, datetime, query, limit, output, show_assets, cloud_cover):
    """
    🛰️ Search for satellite data items with detailed filters.
    
    Find satellite imagery using spatial (bbox), temporal (datetime), and 
    attribute (query) filters. Results can be saved for download or further processing.
    
    \b
    Search Parameters:
    --provider    Choose data source (pc=faster, auto-signed URLs; es=open access)
    --collections Specify datasets to search (use 'ogapi collections list' to see options)
    --bbox        Geographic area of interest in decimal degrees
    --datetime    Time period of interest
    --query       Advanced filters (cloud cover, processing level, etc.)
    --limit       Control result size for performance
    
    \b
    Examples:
      # Basic search in Seattle area:
      ogapi search items -c sentinel-2-l2a -b "-122.5,47.5,-122.0,48.0"
      
      # Search with date range and cloud filter:
      ogapi search items -c sentinel-2-l2a -d "2024-06-01/2024-08-31" --cloud-cover 20
      
      # Advanced query with JSON filter:
      ogapi search items -c sentinel-2-l2a -q '{"eo:cloud_cover":{"lt":15},"platform":{"eq":"sentinel-2a"}}'
      
      # Search multiple collections:
      ogapi search items -c "sentinel-2-l2a,landsat-c2-l2" -b "-120,35,-119,36" -l 20
      
      # Save results for later download:
      ogapi search items -c sentinel-2-l2a -b "bbox" -o search_results.json
    
    \b
    Output Format:
    Results are displayed as a summary and optionally saved as JSON.
    Use saved JSON with download commands for batch processing.
    
    \b
    Provider Notes:
    pc  = Microsoft Planetary Computer (requires auth, faster, auto-signed URLs)
    es  = Element84 EarthSearch (open access, no auth required)
    """
    verbose = ctx.obj.get('verbose', False)
    
    if verbose:
        click.echo(f"🔍 Searching {provider.upper()} for items...")
        click.echo(f"📊 Parameters: collections={collections}, bbox={bbox}, datetime={datetime}")
    
    try:
        # Create client
        if provider == 'pc':
            client = ogapi.planetary_computer(auto_sign=True)
            if verbose:
                click.echo("🌍 Using Planetary Computer with auto-signing")
        else:
            client = ogapi.earth_search()
            if verbose:
                click.echo("🔗 Using EarthSearch open API")
        
        # Parse collections
        collections_list = [c.strip() for c in collections.split(',')]
        if verbose:
            click.echo(f"📁 Searching collections: {collections_list}")
        
        # Add cloud cover to query if specified
        if cloud_cover is not None:
            if query is None:
                query = {}
            query['eo:cloud_cover'] = {'lt': cloud_cover}
            if verbose:
                click.echo(f"☁️ Added cloud cover filter: <{cloud_cover}%")
        
        # Perform search
        click.echo(f"🔍 Searching {provider.upper()}...")
        results = client.search(
            collections=collections_list,
            bbox=bbox,
            datetime=datetime,
            query=query,
            limit=limit
        )
        
        items = results.get_all_items()
        
        if len(items) == 0:
            click.echo("❌ No items found matching search criteria")
            click.echo("\n💡 Try adjusting your search parameters:")
            click.echo("   • Expand the bounding box area")
            click.echo("   • Extend the date range")
            click.echo("   • Increase cloud cover threshold")
            click.echo("   • Check collection names with 'ogapi collections list'")
            return
        
        click.echo(f"\n✅ Found {len(items)} items")
        
        # Display results summary
        if len(items) > 0:
            # Calculate statistics
            cloud_covers = [item.properties.get('eo:cloud_cover') for item in items 
                           if item.properties.get('eo:cloud_cover') is not None]
            
            if cloud_covers:
                avg_cloud = sum(cloud_covers) / len(cloud_covers)
                min_cloud = min(cloud_covers)
                max_cloud = max(cloud_covers)
                click.echo(f"☁️ Cloud cover: {min_cloud:.1f}% - {max_cloud:.1f}% (avg: {avg_cloud:.1f}%)")
            
            # Show date range
            dates = [item.properties.get('datetime') for item in items 
                    if item.properties.get('datetime')]
            if dates:
                click.echo(f"📅 Date range: {min(dates)} to {max(dates)}")
        
        # Display individual items
        for i, item in enumerate(items):
            click.echo(f"\n📄 Item {i+1}: {item.id}")
            click.echo(f"   📁 Collection: {item.collection}")
            click.echo(f"   📅 Date: {item.properties.get('datetime', 'N/A')}")
            
            cloud_cover_val = item.properties.get('eo:cloud_cover')
            if cloud_cover_val is not None:
                click.echo(f"   ☁️ Cloud Cover: {cloud_cover_val:.1f}%")
            
            platform = item.properties.get('platform', item.properties.get('constellation'))
            if platform:
                click.echo(f"   🛰️ Platform: {platform}")
            
            if show_assets:
                assets = item.list_assets()
                if len(assets) <= 8:
                    click.echo(f"   🎯 Assets: {', '.join(assets)}")
                else:
                    click.echo(f"   🎯 Assets: {', '.join(assets[:8])} ... (+{len(assets)-8} more)")
        
        # Save to file if requested
        if output:
            results_data = {
                'search_metadata': {
                    'provider': provider,
                    'collections': collections_list,
                    'bbox': bbox,
                    'datetime': datetime,
                    'query': query,
                    'limit': limit,
                    'items_found': len(items),
                    'search_timestamp': click.get_current_context().meta.get('timestamp')
                },
                'search_params': {
                    'provider': provider,
                    'collections': collections_list,
                    'bbox': bbox,
                    'datetime': datetime,
                    'query': query,
                    'limit': limit
                },
                'items': items.to_list()
            }
            
            with open(output, 'w') as f:
                json.dump(results_data, f, indent=2)
            click.echo(f"\n💾 Results saved to: {output}")
            click.echo(f"💡 Use: ogapi download search-results {output}")
    
    except Exception as e:
        click.echo(f"❌ Search failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        
        click.echo("\n💡 Troubleshooting tips:")
        click.echo("   • Check collection names: ogapi collections list")
        click.echo("   • Verify bbox format: west,south,east,north")
        click.echo("   • Check date format: YYYY-MM-DD or YYYY-MM-DD/YYYY-MM-DD")
        click.echo("   • Validate JSON query syntax")
        raise click.Abort()


@search_group.command('quick')
@click.argument('collection')
@click.argument('location')
@click.option('--provider', '-p',
              type=click.Choice(['pc', 'es'], case_sensitive=False),
              default='pc',
              help='Data provider (default: pc)')
@click.option('--days', '-d',
              type=int,
              default=30,
              help='Number of days back to search (default: 30)')
@click.option('--cloud-cover', '-cc',
              type=float,
              default=30,
              help='Maximum cloud cover percentage (default: 30)')
@click.option('--limit', '-l',
              type=int,
              default=5,
              help='Maximum results to show (default: 5)')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save results to JSON file')
@click.pass_context
def quick_search(ctx, collection, location, provider, days, cloud_cover, limit, output):
    """
    ⚡ Quick search for recent clear data at a specific location.
    
    Simplified interface for common searches. Automatically searches
    the last N days for clear imagery at a given location.
    
    \b
    Arguments:
    COLLECTION  Collection to search (e.g., "sentinel-2-l2a", "landsat-c2-l2")
    LOCATION    Bounding box as "west,south,east,north" 
    
    \b
    Examples:
      # Recent Sentinel-2 data in Seattle:
      ogapi search quick sentinel-2-l2a "-122.5,47.5,-122.0,48.0"
      
      # Last 7 days, very clear imagery:
      ogapi search quick sentinel-2-l2a "bbox" --days 7 --cloud-cover 10
      
      # Landsat data with more results:
      ogapi search quick landsat-c2-l2 "bbox" --limit 10
      
      # Save for later processing:
      ogapi search quick sentinel-2-l2a "bbox" -o recent_data.json
    
    \b
    Location Format:
    Provide bounding box as comma-separated values: west,south,east,north
    Example: "-122.5,47.5,-122.0,48.0" (Seattle area)
    
    \b
    Tips:
    • Use smaller areas for faster results
    • Lower cloud cover values for clearer imagery  
    • Increase days for more search options
    • Try different providers if no results found
    """
    from datetime import datetime, timedelta
    verbose = ctx.obj.get('verbose', False)
    
    try:
        # Parse location
        try:
            bbox = parse_bbox(location)
        except click.BadParameter:
            click.echo("❌ Invalid location format")
            click.echo("💡 Use format: west,south,east,north")
            click.echo("   Example: -122.5,47.5,-122.0,48.0")
            return
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
        
        if verbose:
            click.echo(f"🔍 Quick search parameters:")
            click.echo(f"   Collection: {collection}")
            click.echo(f"   Location: {bbox}")
            click.echo(f"   Date range: {date_range}")
            click.echo(f"   Max cloud cover: {cloud_cover}%")
            click.echo(f"   Provider: {provider.upper()}")
        
        click.echo(f"⚡ Quick search: {collection} (last {days} days, <{cloud_cover}% clouds)")
        
        # Create client and search
        if provider == 'pc':
            client = ogapi.planetary_computer(auto_sign=True)
        else:
            client = ogapi.earth_search()
        
        results = client.search(
            collections=[collection],
            bbox=bbox,
            datetime=date_range,
            query={'eo:cloud_cover': {'lt': cloud_cover}},
            limit=limit
        )
        
        items = results.get_all_items()
        
        if items:
            click.echo(f"\n✅ Found {len(items)} clear items")
            
            # Show best item (lowest cloud cover)
            best_item = min(items, key=lambda x: x.properties.get('eo:cloud_cover', 100))
            click.echo(f"\n🏆 Best item (clearest):")
            click.echo(f"   📄 ID: {best_item.id}")
            click.echo(f"   📅 Date: {best_item.properties.get('datetime')}")
            click.echo(f"   ☁️ Cloud Cover: {best_item.properties.get('eo:cloud_cover'):.1f}%")
            
            # Show all items summary
            if len(items) > 1:
                click.echo(f"\n📋 All {len(items)} items:")
                for i, item in enumerate(items):
                    date = item.properties.get('datetime', '')[:10]  # Just date part
                    cloud = item.properties.get('eo:cloud_cover', 0)
                    click.echo(f"   {i+1}. {date} - {cloud:.1f}% clouds")
            
            # Show usage suggestions
            if output:
                # Save results
                results_data = {
                    'search_params': {
                        'provider': provider,
                        'collections': [collection],
                        'bbox': bbox,
                        'datetime': date_range,
                        'query': {'eo:cloud_cover': {'lt': cloud_cover}},
                        'limit': limit
                    },
                    'items': items.to_list()
                }
                
                with open(output, 'w') as f:
                    json.dump(results_data, f, indent=2)
                click.echo(f"\n💾 Results saved to: {output}")
            
            click.echo(f"\n💡 Next steps:")
            if output:
                click.echo(f"   ogapi download search-results {output}")
            else:
                click.echo(f"   ogapi search items -c {collection} -b \"{location}\" -o results.json")
                click.echo(f"   ogapi download search-results results.json")
        else:
            click.echo(f"❌ No clear items found in the last {days} days")
            click.echo(f"\n💡 Try adjusting search parameters:")
            click.echo(f"   • Increase days: --days {days * 2}")
            click.echo(f"   • Relax cloud cover: --cloud-cover {min(cloud_cover + 20, 80)}")
            click.echo(f"   • Expand area (make bbox larger)")
            if provider == 'pc':
                click.echo(f"   • Try EarthSearch: --provider es")
            else:
                click.echo(f"   • Try Planetary Computer: --provider pc")
    
    except Exception as e:
        click.echo(f"❌ Quick search failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()


@search_group.command('compare')
@click.option('--collections', '-c',
              required=True,
              help='Comma-separated collection names to compare')
@click.option('--bbox', '-b',
              required=True,
              callback=lambda ctx, param, value: parse_bbox(value),
              help='Bounding box as "west,south,east,north"')
@click.option('--datetime', '-d',
              help='Date range as "YYYY-MM-DD/YYYY-MM-DD"')
@click.option('--cloud-cover', '-cc',
              type=float,
              default=50,
              help='Maximum cloud cover percentage (default: 50)')
@click.option('--limit', '-l',
              type=int,
              default=10,
              help='Maximum items per provider (default: 10)')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save comparison results to JSON file')
@click.pass_context
def compare_providers(ctx, collections, bbox, datetime, cloud_cover, limit, output):
    """
    🔄 Compare data availability between Planetary Computer and EarthSearch.
    
    Search the same parameters on both providers to compare:
    - Number of available items
    - Date coverage
    - Cloud cover distribution
    - Asset availability
    
    \b
    Examples:
      # Compare Sentinel-2 availability:
      ogapi search compare -c sentinel-2-l2a -b "-122,47,-121,48"
      
      # Compare with date range:
      ogapi search compare -c sentinel-2-l2a -d "2024-06-01/2024-08-31" -b "bbox"
      
      # Compare multiple collections:
      ogapi search compare -c "sentinel-2-l2a,landsat-c2-l2" -b "bbox" -o comparison.json
    
    \b
    Use Cases:
    • Choose best provider for your area/timeframe
    • Understand data availability differences
    • Plan multi-provider workflows
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        collections_list = [c.strip() for c in collections.split(',')]
        
        click.echo(f"🔄 Comparing providers for:")
        click.echo(f"   📁 Collections: {', '.join(collections_list)}")
        click.echo(f"   📍 Area: {bbox}")
        if datetime:
            click.echo(f"   📅 Period: {datetime}")
        click.echo(f"   ☁️ Max clouds: {cloud_cover}%")
        
        search_params = {
            'collections': collections_list,
            'bbox': bbox,
            'datetime': datetime,
            'query': {'eo:cloud_cover': {'lt': cloud_cover}},
            'limit': limit
        }
        
        results = {}
        
        # Search Planetary Computer
        try:
            if verbose:
                click.echo("\n🌍 Searching Planetary Computer...")
            pc = ogapi.planetary_computer(auto_sign=True)
            pc_results = pc.search(**search_params)
            pc_items = pc_results.get_all_items()
            results['planetary_computer'] = {
                'items_found': len(pc_items),
                'items': pc_items.to_list() if pc_items else []
            }
            click.echo(f"🌍 Planetary Computer: {len(pc_items)} items")
        except Exception as e:
            results['planetary_computer'] = {'error': str(e), 'items_found': 0}
            click.echo(f"❌ Planetary Computer error: {e}")
        
        # Search EarthSearch
        try:
            if verbose:
                click.echo("🔗 Searching EarthSearch...")
            es = ogapi.earth_search()
            es_results = es.search(**search_params)
            es_items = es_results.get_all_items()
            results['earthsearch'] = {
                'items_found': len(es_items),
                'items': es_items.to_list() if es_items else []
            }
            click.echo(f"🔗 EarthSearch: {len(es_items)} items")
        except Exception as e:
            results['earthsearch'] = {'error': str(e), 'items_found': 0}
            click.echo(f"❌ EarthSearch error: {e}")
        
        # Comparison summary
        pc_count = results['planetary_computer']['items_found']
        es_count = results['earthsearch']['items_found']
        
        click.echo(f"\n📊 Comparison Summary:")
        click.echo(f"   🌍 Planetary Computer: {pc_count} items")
        click.echo(f"   🔗 EarthSearch: {es_count} items")
        
        if pc_count > 0 and es_count > 0:
            if pc_count > es_count:
                click.echo(f"   🏆 PC has {pc_count - es_count} more items")
            elif es_count > pc_count:
                click.echo(f"   🏆 ES has {es_count - pc_count} more items")
            else:
                click.echo(f"   🤝 Both providers have equal coverage")
        
        # Save results
        if output:
            comparison_data = {
                'search_params': search_params,
                'comparison_timestamp': datetime.now().isoformat(),
                'results': results
            }
            
            with open(output, 'w') as f:
                json.dump(comparison_data, f, indent=2)
            click.echo(f"\n💾 Comparison saved to: {output}")
        
        # Recommendations
        click.echo(f"\n💡 Recommendations:")
        if pc_count > es_count:
            click.echo("   • Use Planetary Computer for this search")
            click.echo("   • PC offers more data coverage")
        elif es_count > pc_count:
            click.echo("   • Use EarthSearch for this search")
            click.echo("   • ES offers more data coverage")
        else:
            click.echo("   • Both providers offer similar coverage")
            click.echo("   • Choose based on your workflow needs")
    
    except Exception as e:
        click.echo(f"❌ Comparison failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()
