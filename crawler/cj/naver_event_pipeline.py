#!/usr/bin/env python3
"""
Naver Event Data Pipeline
Complete pipeline: Crawl images -> Extract OCR data -> Save to Supabase
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from naver_brand_image_crawler import NaverBrandImageCrawler
from naver_event_ocr_extractor import NaverEventOCRExtractor
from save_to_supabase import SupabaseSaver


class NaverEventPipeline:
    """Complete pipeline for Naver event data extraction"""

    def __init__(self, output_dir='naver_event_output'):
        self.output_dir = output_dir
        Path(output_dir).mkdir(exist_ok=True)

        self.crawler = NaverBrandImageCrawler(f'{output_dir}/images')
        self.extractor = NaverEventOCRExtractor()
        self.saver = SupabaseSaver()

    def run(self, url: str, target_class: str = 'se-main-container', save_to_db: bool = True) -> Dict:
        """
        Run the complete pipeline

        Args:
            url: Naver Brand page URL
            target_class: CSS class of div containing images
            save_to_db: Whether to save to Supabase database

        Returns:
            Dictionary with pipeline results
        """
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║          Naver Event Data Extraction Pipeline                    ║
╚══════════════════════════════════════════════════════════════════╝

URL: {url}
Target Div Class: {target_class}
Save to Database: {save_to_db}
        """)

        results = {
            'success': False,
            'url': url,
            'crawl_result': None,
            'extraction_result': None,
            'save_result': None,
            'error': None
        }

        try:
            # Step 1: Crawl images
            print("\n" + "="*70)
            print("STEP 1: 이미지 크롤링")
            print("="*70)

            crawl_result = self.crawler.crawl(url, target_class)
            results['crawl_result'] = crawl_result

            if not crawl_result['success']:
                results['error'] = f"Image crawling failed: {crawl_result.get('error')}"
                return results

            if not crawl_result['downloaded_images']:
                results['error'] = "No images downloaded"
                return results

            print(f"\n✓ {len(crawl_result['downloaded_images'])}개 이미지 다운로드 완료")

            # Step 2: Extract text using OCR
            print("\n" + "="*70)
            print("STEP 2: OCR 텍스트 추출")
            print("="*70)

            texts = self.extractor.extract_all_text(crawl_result['downloaded_images'])

            # Step 3: Parse event information
            print("\n" + "="*70)
            print("STEP 3: 이벤트 정보 파싱")
            print("="*70)

            brand_name = crawl_result['page_info'].get('brand_name', '').upper()
            event_data = self.extractor.parse_event_info(texts, url, brand_name)

            # Save extraction results to JSON
            output_file = f"{self.output_dir}/event_data.json"
            self.extractor.save_results(event_data, texts, output_file)

            results['extraction_result'] = {
                'event_data': event_data,
                'output_file': output_file
            }

            # Step 4: Save to Supabase (optional)
            if save_to_db:
                print("\n" + "="*70)
                print("STEP 4: Supabase 데이터베이스 저장")
                print("="*70)

                save_result = self.saver.save_event(
                    event_data=event_data,
                    image_urls=crawl_result['image_urls'],
                    raw_ocr_data={os.path.basename(k): v for k, v in texts.items()}
                )

                results['save_result'] = save_result

                if not save_result['success']:
                    print(f"\n⚠ 데이터베이스 저장 실패: {save_result['error']}")
                    print("   (이벤트 데이터는 JSON 파일로 저장되었습니다)")
            else:
                print("\n⚠ 데이터베이스 저장 건너뛰기 (--no-save 옵션)")

            results['success'] = True

            # Final summary
            print("\n" + "="*70)
            print("파이프라인 완료")
            print("="*70)
            print(f"\n✅ 성공!")
            print(f"\n결과 요약:")
            print(f"  - 다운로드된 이미지: {len(crawl_result['downloaded_images'])}개")
            print(f"  - 이벤트 제목: {event_data.get('event_title', 'N/A')}")
            print(f"  - 브랜드: {event_data.get('brand_name', 'N/A')}")
            print(f"  - 이벤트 기간: {event_data.get('event_date', 'N/A')}")
            print(f"  - 금액대별 혜택: {len(event_data.get('benefits_by_purchase_amount', []))}개")
            print(f"  - 쿠폰 혜택: {len(event_data.get('coupon_benefits', []))}개")
            print(f"\n출력 파일:")
            print(f"  - 이미지: {self.crawler.output_dir}/")
            print(f"  - 데이터: {output_file}")

            if save_to_db and results['save_result'] and results['save_result']['success']:
                print(f"  - DB ID: {results['save_result']['data']['id']}")

            return results

        except Exception as e:
            print(f"\n❌ 파이프라인 오류: {e}")
            import traceback
            traceback.print_exc()

            results['error'] = str(e)
            return results


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Naver Event Data Extraction Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract event data from a Naver Brand page
  python naver_event_pipeline.py --url "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684"

  # Extract without saving to database
  python naver_event_pipeline.py --url "..." --no-save

  # Specify custom div class
  python naver_event_pipeline.py --url "..." --div-class "custom-container"
        """
    )

    parser.add_argument(
        '--url',
        type=str,
        required=True,
        help='Naver Brand page URL'
    )

    parser.add_argument(
        '--div-class',
        type=str,
        default='se-main-container',
        help='CSS class of div containing images (default: se-main-container)'
    )

    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save to Supabase database'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='naver_event_output',
        help='Output directory for images and data (default: naver_event_output)'
    )

    args = parser.parse_args()

    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Run pipeline
    pipeline = NaverEventPipeline(output_dir=args.output_dir)
    results = pipeline.run(
        url=args.url,
        target_class=args.div_class,
        save_to_db=not args.no_save
    )

    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)


if __name__ == '__main__':
    main()
